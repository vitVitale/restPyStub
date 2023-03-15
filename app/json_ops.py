import re
from rstr import xeger
from app.dto import JPath
# TODO:: standard library is too slow !!
# from jsonpath_ng import parse
# from jsonpath_ng.ext import parse
from yaml import safe_load as boolean
from jpath_finder.jpath_parser import find
from json import loads, dumps, JSONDecodeError


def validate_by_jsonpath(search: str, dom: JPath, target):
    search_target = target
    if search in ['inHeaders', 'inParams']:
        search_target = dumps(dict(target.items()), ensure_ascii=False)
    if dom.__getattribute__(search):
        for check in dom.__getattribute__(search):
            # actual = parse(check['path']).find(loads(search_target))[0].value
            actual = find(check['path'], loads(search_target))[0]
            expected = check['value']
            if isinstance(expected, dict):
                keys = list(expected.keys())
                if len(keys) == 1 and keys[0].startswith('$'):
                    if keys[0] == '$regex':
                        assert bool(re.search(pattern=expected[keys[0]], string=actual))
                    continue
            assert (actual == expected)


def perform_replacement(outgoing_body: dict, incoming_body: str, incoming_headers):
    incoming_headers = loads(dumps(dict(incoming_headers.items()), ensure_ascii=False))
    text = dumps(outgoing_body, ensure_ascii=False)
    try:
        incoming_body = loads(incoming_body)
    except JSONDecodeError:
        return outgoing_body
    temp_text = text
    render_injections_set = set(re.findall('("<< jPathFromRq(Body|Headers)\((.+?)\) >>")', temp_text))
    render_generations_set = set(re.findall('("<< gen(Integer|Float|String|Boolean)ByRegex\((.+?)\) >>")', temp_text))
    for template, instruction, path in render_injections_set:
        try:
            rendered = None
            if instruction == 'Body':
                # results = [x.value for x in parse(path).find(incoming_body)]
                # rendered = results if len(results) > 1 else results[0]
                results = find(path, incoming_body)
                rendered = results if len(results) > 1 else results[0]
            if instruction == 'Headers':
                # rendered = parse(path).find(incoming_headers)[0].value
                rendered = find(path, incoming_headers)[0]
            temp_text = temp_text.replace(template, dumps(rendered))
        except Exception as exc: continue
    for template, instruction, regex in render_generations_set:
        try:
            rendered = xeger(regex.replace('\\\\', '\\'))
            if instruction == 'Integer': rendered = int(rendered)
            if instruction == 'Float': rendered = float(rendered)
            if instruction == 'Boolean': rendered = boolean(rendered)
            temp_text = temp_text.replace(template, dumps(rendered))
        except Exception as exc: continue
    return loads(temp_text)
