@contextmanager
def tenant(value):
    """
        Context manager for tenants. Used to set and cleanup tennant.
        param, value, can be Tenant object or id.
        Using the context context manager
        ```python
        with tenant(1):
            Profile.objects.get(pk=1)
        ```
        Using it as a decorator
        ```python
        @tenant(1)
        def foo():
            Profile.object.get(pk=1)
        ```
    """

    previous = get_current_tenant_id()
    set_tenant_id(value)

    try:
        yield
    finally:
        set_tenant_id(previous)
