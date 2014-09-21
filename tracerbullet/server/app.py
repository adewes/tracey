from flask import (Flask,
                  render_template,
                  make_response,
                  Response,
                  redirect
                  )

from .settings import render_context,project_path,template_folder,static_folder
from .decorators import with_session

from multiprocessing import Process,Queue
import signal
import sys
import pygments
from collections import defaultdict
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

class ServerProcess(Process):

    def __init__(self,*args,**kwargs):
        super(ServerProcess,self).__init__(*args,**kwargs)
        self.command_queue = Queue()
        self.response_queue = Queue()

    def run(self):
        app.server = self
        sys.stdin.close()
        signal.signal(signal.SIGINT,signal.SIG_IGN)
        try:
            app.run(debug = True,host = '0.0.0.0',port = 8888,use_reloader = False)
        except KeyboardInterrupt:
            exit(0)

from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app = Flask(__name__,
            static_url_path = render_context['static_url'],
            static_folder = project_path+static_folder,
            template_folder = project_path+template_folder)

app.url_map.converters['regex'] = RegexConverter

@app.route('/static/css/code-styles.css')
@with_session()
def code_styles():
    return Response(HtmlFormatter().get_style_defs('.highlight'),mimetype = 'text/css')


@app.route('/add<regex(".*"):code_id>')
@with_session()
def add(code_id):
    app.server.command_queue.put(["add_code",code_id])
    app.server.response_queue.get()
    return redirect("/")

@app.route('/remove<regex(".*"):code_id>')
@with_session()
def remove(code_id):
    app.server.command_queue.put(["remove_code",code_id])
    app.server.response_queue.get()
    return redirect("/")

@app.route('/')
@with_session()
def index():
    app.server.command_queue.put(["get_profile"])
    result = app.server.response_queue.get()
    context = {'profiles' : []}
    tracked_code_ids = dict([(profile['code_id'],True) for profile in result['profiles']])
    for profile in result['profiles']:
        source = "\n".join(profile['source'][0])
        first_line,last_line = profile['source'][1]
        formatted_lines = pygments.highlight(source,PythonLexer(),HtmlFormatter(nowrap = True)).split("\n")
        while True:
            if not formatted_lines:
                break
            if not formatted_lines[-1]:
                formatted_lines = formatted_lines[:-1]
            else:
                break
        profile['code'] = "\n".join(formatted_lines)
        profile['timings'] = [profile['times'][first_line+i] if first_line+i in profile['times'] else None for i in range(0,len(formatted_lines))]
        context['profiles'].append(profile)
        profile['adjacent_code'] = defaultdict(list)
        for adjacent_code in result['adjacent_code']:
            if adjacent_code['referer'] == profile['code_id']:
                if adjacent_code['code_id'] in tracked_code_ids:
                    adjacent_code['tracked'] = True
                else:
                    adjacent_code['tracked'] = False
                profile['adjacent_code'][adjacent_code['line_number']].append(adjacent_code)
    context.update(render_context)
    response = make_response(render_template("index.html",**context))
    return response
