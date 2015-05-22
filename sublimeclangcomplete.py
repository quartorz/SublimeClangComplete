import sublime, sublime_plugin

import os
import subprocess
import functools

import SublimeClangComplete.clang as clang
import SublimeClangComplete.clang.cindex


def load_settings():
    return sublime.load_settings("SublimeClangComplete.sublime-settings")

def make_opitons():
    result = load_settings().get('options')

    for i in load_settings().get('include_paths'):
        result.extend((b'-I', i.encode('utf-8')))

    return result

class CompletionEventListener(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if len(locations) == 0:
            return []

        settings = load_settings()
        filename = view.file_name()

        if os.path.splitext(filename)[-1] not in settings.get('extensions'):
            return []

        if not clang.cindex.Config.loaded:
            clang.cindex.Config.set_compatibility_check(False)
            clang.cindex.Config.set_library_path(load_settings().get('clang_path'))

        content = view.substr(sublime.Region(0, view.size()))

        index = clang.cindex.TranslationUnit.from_source(
            filename.encode('utf-8'),
            make_opitons(),
            [(filename.encode('utf-8'), content.encode('utf-8'))])

        row, col = view.rowcol(locations[0])

        c = index.codeComplete(
            filename.encode('utf-8'),
             row + 1,
             col + 1,
             [(filename.encode('utf-8'), content.encode('utf-8'))])

        completion = []

        for i in c.results:
            signature = ''
            result = ''
            text = ''
            for j in i.string:
                if j.isKindResultType():
                    result = j.spelling.decode('utf-8')
                else:
                    signature += j.spelling.decode('utf-8')
                if j.isKindTypedText():
                    text = j.spelling.decode('utf-8')
            completion.append((signature + '\t' + result, text))

        return completion