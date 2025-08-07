
import ast
import inspect
from cloudpickle.cloudpickle import _extract_code_globals
from typing import List

def walk_special(node):
    from collections import deque
    todo = deque([node])
    top_level_node = node
    while todo:
        node = todo.popleft()
        # Added this conditional
        if isinstance(node, ast.FunctionDef):
            if node not in ast.iter_child_nodes(top_level_node):
                continue
        todo.extend(ast.iter_child_nodes(node))
        yield node

def contains_explicit_return(f):
    source = inspect.getsource(f).lstrip()
    parsed = ast.parse(source)
    for node in walk_special(parsed):
        if isinstance(node, ast.Return):
            return True
    return False

def _convert(v, _ptype):
    exception = False
    if _ptype.annotation==bool:
        if type(v)==list:
            v = v[0]
        if v.lower() == 'true':
            return True
        elif v.lower() == 'false':
            return False
        else:
            exception = True
            
    elif _ptype.annotation==str:
        if type(v)==list:
            v = v[0]
    elif _ptype.annotation==int:
        if type(v)==list:
            v = v[0]
        try:
            return int(v)
        except:
            exception = True
            
    elif _ptype.annotation==float:
        if type(v)==list:
            v = v[0]
        try:
            return float(v)
        except:
            exception = True          
    if exception:
        raise Exception(f'Value {v} for Parameter {_ptype.name} is not valid. Need value of type {_ptype.annotation} ')
    else:
        return v

def patched(f, _globals = {}):
    """
    This function opens up the function and adds a return statement of the locals for state tracking

    Args:
        f (function): The function to patch
        _globals (dict, optional): The globals to use. Defaults to {}.        
    
    Returns:
        function: The patched function
    """
    source = inspect.getsource(f).lstrip()
    tree = ast.parse(source)
    new_body = [
        *tree.body[0].body,
        
        ast.parse('return {**locals()}').body[0]
    ]
    tree.body[0].body = new_body
    code = compile(tree,filename=f.__code__.co_filename,mode='exec')
    namespace = {}
    mod = inspect.getmodule(f)
    cd = f.__code__
    _new_globals = {
        k :  f.__globals__[k] for k in _extract_code_globals(cd) if k in  f.__globals__ 
    }
    _globals = {**_globals, **_new_globals, 'List' : List}
    exec(code,_globals, namespace)
    _g = namespace[f.__name__]

    return _g    




def shareable_wrapper(
        func, 
        title ,
        layout = 'centered', 
        icon = None, 
        patch = True, 
        _globals = {}, 
        sidebar_state = 'collapsed'
    ): 
    import inspect
    import os
    import streamlit as st

    # Set _sidebar_state
    if '_sidebar_state' not in st.session_state:
        st.session_state._sidebar_state = sidebar_state

    # Set page config
    st.set_page_config(
        layout=layout, 
        initial_sidebar_state=st.session_state._sidebar_state, 
        page_title = title,
        page_icon = icon,
    )
        
    def _fun(**kwargs):
        pass

    import os
    # Rewrite code with patched function
    if patch:
        if contains_explicit_return(func):
            raise Exception(f'{func.__name__} cannot contain explicit return.')
        _patched_function = patched(func, _globals)
    else:
        _patched_function = func 

    
    if st.__version__ < '1.37.0':
        st.fragment = st.experimental_fragment
        
    def _func(**kwargs):
        import streamlit as st
        # Get the defautls arguments 
        argspec = inspect.signature(func)
        # Extract defaults
        defaults = {
            k : v for k,v in argspec.parameters.items() if v.default!=inspect._empty
        }        
        
    
        if True:
            # Load query params
            query_params = {k: st.query_params.get_all(k) for k in st.query_params.keys()}

            # If not in query params, but in session state append it to query params 
            for k in defaults.keys():
                if k not in query_params and k in st.session_state:
                    query_params[k] = [st.session_state.get(k)]

            for k, v in defaults.items():
                if v.annotation!=list:
                    if v.annotation==bool:
                        tv = bool(query_params.get(k, [v.default])[0]  )
                    elif v.annotation == int:
                        tv = int(query_params.get(k, [v.default])[0])
                    else:
                        tv = query_params.get(k, [v.default])[0]
                else:
                    tv = query_params.get(k, [])  
                if tv is not None:
                    st.session_state[k] = _convert(tv, v)
                else:
                    st.session_state[k] = v.default
            _state = {**st.session_state}
            res = _patched_function(**_state)
        
            
            for k,v  in res.items(): 
                if k in defaults:
                    st.query_params[k] = v  
                    st.session_state[k] = v
        
        return res
    return _func



def shareable(
            f, 
            name = None,
            layout : str = 'centered',
            title : str = None,
            icon : str = None,
            sidebar_state : str = 'auto',
            _globals : dict = {}
    ):

    """
    Deploy a streamlit app from a function

    Args:
        f (function): The function to deploy
        name (str, optional): The name of the app. Defaults to None.
        layout (str, optional): The layout of the app. Defaults to 'wide' alternatively can use 'centered'.
        title (str, optional): The title of the app. Defaults to None.
        icon (str, optional): The icon of the app. Defaults to None.
        sidebar_state (str, optional): The state of the sidebar. Defaults to 'collapsed'. (can use auto or expanded)
        _globals (dict, optional): The globals to use. Defaults to {}.
    """
    # Parse name if needed
    if not name:
        name = f.__name__
    if not title:
        title = name
    
    shareable_wrapper(
        f, title = title, _globals = _globals, layout = layout, icon = icon, 
        sidebar_state = sidebar_state
    )()
