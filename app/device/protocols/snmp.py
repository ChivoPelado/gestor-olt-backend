from pysnmp import hlapi
from celery import shared_task


#@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
#             name='olt:get_request')
def get_request(target, oids, credential, port):
    return get(target, oids, hlapi.CommunityData(credential), port)


def get_bulk_request(target, oid, credential, port):
    return next_cmd(target, oid, hlapi.CommunityData(credential), port)


def construct_object_types(list_of_oids):
    object_types = []
    for oid in list_of_oids:
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
    return object_types


def get(target, oids, credentials, port, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types(oids)
    )
    return fetch(handler, 1)[0]


def next_cmd(target, oid, credentials, port, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    response = []
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in hlapi.nextCmd(engine,
                                    credentials,
                                    hlapi.UdpTransportTarget((target, port)),
                                    context,
                                    hlapi.ObjectType(hlapi.ObjectIdentity(oid)),
                                    lexicographicMode=False):
        if errorIndication or errorStatus:
            print(errorIndication or errorStatus)
            break
        else:
            response.append(varBinds)

    return response


def fetch(handler, count):
    response = []
    for i in range(count):
        try:
            error_indication, error_status, error_index, var_binds = next(handler)
            if not error_indication and not error_status:
                items = {}
                for var_bind in var_binds:
                    items[str(var_bind[0])] = cast(var_bind[1])
                response.append(items)
            else:
                return response
                # raise RuntimeError('got SNMP error: {0}'.format(error_indication))
        except StopIteration:
            break
    return response


def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value
