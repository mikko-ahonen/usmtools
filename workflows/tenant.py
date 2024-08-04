import threading

#from .models import Tenant

_threadlocal = threading.local()

def set_tenant_id(id):
    #print("[" + str(threading.get_ident()) + "] Setting tenant id to " + str(id))
    _threadlocal.tenant = {"tenant_id": id}

def full_stack():
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

def current_tenant_id():
    try:
        #print("[" + str(threading.get_ident()) + "] Returning tenant id " + str(_threadlocal.tenant["tenant_id"]))
        #if not hasattr(_threadlocal, 'tenant'):
        #    print(full_stack())
        return _threadlocal.tenant["tenant_id"]
    except Exception as e:
        #print("[" + str(threading.get_ident()) + "] Tenant id not set")
        #print(full_stack())
        return None
        raise Exception(
            """
                Tenant is not set. Use `set_tenant`, to set the tenant before running any queries
                from workflows.tenant import set_tenant
            """
        )
