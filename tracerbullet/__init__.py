from __future__ import absolute_import

from functools import wraps

import tracerbullet.profiler as profiler
import tracerbullet.helpers as helpers
from tracerbullet.models import Project

active_profiler = None

def profile(path = None,include = [],include_names = [],include_ids = [],reset = False,save_profile = False):

    def decorator(f):
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            global active_profiler
            if not active_profiler:
                active_profiler = create_profiler(path = path)
            if reset:
                active_profiler.reset()
            active_profiler.add_code(f.__code__)
            for fn in include:
                active_profiler.add_code_by_function(fn)
            for code_id in include_ids:
                active_profiler.add_code_by_id(code_id)
            for code_name in include_names:
                active_profiler.add_code_by_name(code_name)
            active_profiler.start(add_caller = False)
            res = f(*args,**kwargs)
            active_profiler.stop()

            if save_profile:
                with open(outfile,"wb") as output_file:
                    output_file.write(json.dumps(profile,indent = 2))
                active_profiler.project.save_profile(active_profiler.processed_profile)

            return res

        return decorated_function

    return decorator

def get_profiler():
    global active_profiler
    return active_profiler

def create_profiler(path = None):

    project_path = helpers.get_project_path(path)
    if not project_path:
        raise IOError("no profiler configuration found!")
    project = Project(project_path+"/.tracerbullet")
    project.load()
    return profiler.Profiler(project_config)
