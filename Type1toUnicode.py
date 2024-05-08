import logging, os, datetime
from json import load, JSONDecodeError
from sys import exit
from jellyfish import jaro_winkler_similarity # type: ignore
from Levenshtein import ratio as lev_ratio # type: ignore
from argparse import ArgumentParser
from pypdf import PdfReader, PdfWriter # type: ignore
from pypdf.generic import NameObject, StreamObject # type: ignore

NAME = 'Type1toUnicode'
VERSION = '0.3.0'
SUB_TYPE = 'Type1'
TEMPLATE = \
"""
/CIDInit /ProcSet findresource begin 12 dict begin begincmap /CIDSystemInfo <<
/Registry ({name}+0) /Ordering (T1UV) /Supplement 0 >> def
/CMapName /{name}+0 def
/CMapType 2 def
1 begincodespacerange <{fchar_hex}> <{lchar_hex}> endcodespacerange
{lchar_dec} beginbfchar
{mapping}
endbfchar
endcmap CMapName currentdict /CMap defineresource pop end end
"""
class CustomArgumentParser(ArgumentParser):
    def error(self, message):
        print(f"{NAME} \nversion: {VERSION}\n\n{message}")
        self.print_help()
        self.exit(1)

class UnicodeMapper:
    @classmethod
    def get_unicode_value(cls, data, font_name, property_name):
        for font in data.get('fonts', []):
            if font.get('name') == font_name:
                return font.get('data', {}).get(property_name, None)
        return None
    
    @classmethod
    def find_similar_font(cls, font_dict, search_font):
        similarity, return_font = 0, None
        for font_name, mapped_name in font_dict.items():
            jw_sim = jaro_winkler_similarity(font_name, search_font) * 100
            if (jw_sim > similarity) and jw_sim>=70:
                similarity, return_font = jw_sim, mapped_name
            if(jw_sim < 45 and (lev_ratio(font_name, search_font)*100)>40):
                similarity, return_font = jw_sim, mapped_name
        return return_font
    
class File:

    @classmethod
    def load_json(cls, filename, encoding='utf-8'):
        with open(filename, 'r', encoding=encoding) as json_file:
            return load(json_file)

    @classmethod
    def validate(cls, filename, extension):
        try:
            if not os.path.exists(filename):
                print(f"File does not exist: {filename}")
                exit(2)

            _, file_extension = os.path.splitext(filename)
            if file_extension.lower() != extension.lower():
                print(f"File is not in expected format. Expected {extension}")
                exit(3)

            if file_extension.lower() == '.json':
                with open(filename, 'r', encoding='utf-8') as json_file:
                    load(json_file)
        except JSONDecodeError:
            print(f"Error in parsing JSON file: {filename}")
            exit(4)
        except Exception as e:
            print("An exception occurred: ", e)
            exit(5)
    
    @classmethod
    def update_metadata(cls, existing_metadata):
        now = datetime.datetime.now()
        formatted_time = 'D:' + now.strftime('%Y%m%d%H%M%S')
        new_metadata = {
            '/ModDate': formatted_time,
            '/Producer': NAME + " " + VERSION
        }

        updated_metadata = existing_metadata.copy()
        updated_metadata.update(new_metadata)
        return updated_metadata

def main():

    cnt_fonts = cnt_skipped = cnt_rep_part = cnt_rep_comp = 0
    error_unicode = None
    argparser = CustomArgumentParser()
    argparser.add_argument('-p', '--pdf_file', type=str, required=True, help='Defines the path to the .pdf file')
    argparser.add_argument('-f', '--font_map', type=str, required=True, help='Defines the path to the .json file')
    argparser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output (prints more information)')
    args = argparser.parse_args()

    File.validate(args.pdf_file, '.pdf')
    File.validate(args.font_map, '.json')

    reader = PdfReader(args.pdf_file)
    metadata = reader.metadata
    
    writer = PdfWriter()

    logger = logging.getLogger("PdfRepair")
    logger.setLevel(logging.DEBUG)
    log_directory = os.path.join (os.getcwd(), 'Log')
    file_handler = logging.FileHandler(os.path.join(log_directory, f'{args.pdf_file[:-4]}_LOG.txt'), delay=True)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    json_data = File.load_json(args.font_map)
    font_dict = {}
    for font in json_data['fonts']:
        font_dict[font['name']] = font['name']
        if 'alternativeNames' in font:
            for alt_name in font['alternativeNames']:
                font_dict[alt_name] = font['name']

    for pagenum, page in enumerate(reader.pages):
        if '/Font' not in page['/Resources']:
            if args.verbose:
                    logger.debug('Page "%s" -> no Font objects on the page -> skipping', pagenum+1)
            continue
        for font, data in page['/Resources']['/Font'].items():
            cnt_fonts += 1
            _dataobj = data.get_object()
            _subtype = _dataobj['/Subtype']
            _fontname = _dataobj['/BaseFont']
            if SUB_TYPE not in _subtype:
                if args.verbose:
                    logger.debug('Page "%s" -> Font "%s" -> other type than Type1 -> "%s" -> skipping', pagenum+1, _fontname, _subtype)
                cnt_skipped += 1
                continue
            if '/Encoding' not in _dataobj or '/Differences' not in _dataobj['/Encoding']:
                if args.verbose:
                    logger.debug('Page "%s" -> Font "%s" -> table Differences does not exists -> skipping', pagenum+1, _fontname)
                cnt_skipped += 1
                continue

            if '/FirstChar' not in _dataobj or '/LastChar' not in _dataobj:
                if args.verbose:
                    logger.debug('Page "%s" -> Font "%s" -> character informations do not exist -> skipping', pagenum+1, _fontname)
                cnt_skipped += 1
                continue

            fchar = _dataobj['/FirstChar']
            lchar = _dataobj['/LastChar']

            if ((lchar+1)-(fchar-1)) != len(_dataobj['/Encoding']['/Differences']):
                if args.verbose:
                    logger.debug('Page "%s" -> Font "%s" -> no ToUnicode but Differences incomplete -> skipping', pagenum+1, _fontname)
                cnt_skipped += 1
                continue

            if '/ToUnicode' in _dataobj['/Encoding']:
                if args.verbose:
                    logger.debug('Page "%s" -> Font "%s" -> ToUnicode already exists -> skipping', pagenum+1, _fontname)
                cnt_skipped += 1
                continue

            mapped_fontname = UnicodeMapper.find_similar_font(font_dict, _fontname)
            if mapped_fontname is None:
                if args.verbose:
                    logger.debug('Page "%s" -> Font "%s" -> no matching mapping name found in JSON file -> skipping', pagenum+1, _fontname)
                cnt_skipped += 1
                continue

            if mapped_fontname is not None and mapped_fontname not in _fontname:
                logger.debug('Page "%s" -> Font "%s" -> mapping assigned, but font name is not in the mapping -> assigned mapping: "%s"', pagenum+1, _fontname, mapped_fontname)

            fchar_hex = f"{fchar:X}".zfill(2)
            lchar_hex = f"{lchar:X}".zfill(2)
            name = f"PAGE{pagenum+1}+{font[1:]}"
            _mapping = []
            for idx, char in enumerate(_dataobj['/Encoding']['/Differences'][1:]):
                char = char[1:]
                idx = (f"{(idx+fchar):X}".zfill(2))
                unicode_value = UnicodeMapper.get_unicode_value(json_data, mapped_fontname, char)
                if unicode_value is None:                                        
                    logger.debug('Page "%s" -> Font "%s" -> Glyph "%s" not found in mapping', pagenum+1, _fontname, char)
                    _mapping.append(f"<{idx}> <0020>")
                    error_unicode = True
                    continue
                _mapping.append(f"<{idx}> <{unicode_value}>")

            if error_unicode is True:
                cnt_rep_part += 1
                error_unicode = False
            else:
                cnt_rep_comp +=1

            _mapping = '\n'.join(_mapping)
            _stream_data = StreamObject()
            _stream_data.set_data(
                bytes(
                    TEMPLATE.format(
                        name=name,
                        fchar_hex=fchar_hex,
                        lchar_hex=lchar_hex,
                        lchar_dec=(lchar-fchar)+1,
                        mapping=_mapping
                    ),
                    encoding='utf-8'
                )
            )
            _stream_data.flate_encode()

            _dataobj.get_object().update(
                {
                    NameObject('/ToUnicode'): _stream_data
                }
            )
    if cnt_rep_comp != 0 or cnt_rep_part !=0:
        for page in reader.pages:
                 writer.add_page(page)
        writer.add_metadata(File.update_metadata(metadata))
        outfile = args.pdf_file.split('.')[0] + '_repaired.pdf'
        with open(outfile, 'wb') as output_pdf:
            writer.write(output_pdf)

        if args.verbose:
            logger.debug('File "%s", "%s" fonts found, "%s" fonts skipped, "%s" fonts repaired partially, "%s" fonts repaired completely', args.pdf_file, cnt_fonts, cnt_skipped, cnt_rep_part, cnt_rep_comp)
        if cnt_rep_part > 0:
            print(f'Some font(s) have undefined character(s) mapping, please see log file {args.pdf_file[:-4]}_log.txt in Log directory.')
    else:
        print("No output PDF file created!")
    print(f'File {args.pdf_file}, {cnt_fonts} fonts found, {cnt_skipped} fonts skipped, {cnt_rep_part} fonts repaired partially, {cnt_rep_comp} fonts repaired completely')

if __name__ == '__main__':
    main()