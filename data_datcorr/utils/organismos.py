# utils/organismos.py

MAPA_SCHEMA = {
    "IPS": "ips",
    "PEDIATRICO": "pediatrico",
    "IGPJ_LISTADO_NUEVO": "igpj_listado_nuevo",
    "IGPJ TXT LISTADO": "igpj_txt_listado",
    "IGPJ": "igpj",
    "MATERNIDAD": "maternidad",
    "ESCRIBANIA": "escribania",
}

MAPEO_COLUMNAS_POR_ORGANISMO = {
    "PEDIATRICO": [
        "caja", "estado", "caratula", "egreso", "ingreso",
        "observaciones", "fecha", "denominacion", "hh_cc", "documento",
    ],
    "MATERNIDAD": [
        "caja", "estado", "caratula", "expediente", "ingreso",
        "egreso", "observaciones", "denominacion", "documento", "fecha",
    ],
    "IPS": [
        "denominacion", "expediente", "documento", "caratula", "estado",
        "caja", "n_lote", "ingreso", "egreso", "ultimo_movimiento",
    ],
    "IGPJ": [
        "denominacion", "departamento", "expediente", "estado", "caratula",
        "ingreso", "egreso", "observaciones", "caja",
    ],
    "IGPJ_LISTADO_NUEVO": [
        "carpetas", "caja", "observacion", "prefijo", "legajo",
        "localidad", "entidad", "anio", "expediente", "documento",
        "estado", "ingreso", "egreso",
    ],
    "ESCRIBANIA": [
        "estado", "ingreso", "egreso", "observaciones", "caja",
        "localidad", "legajo", "nombre_apellido", "timbrado_fiscal",
    ],
}


def schema_para_base(base: str) -> str:
    return MAPA_SCHEMA[base]


def columnas_para_base(base: str) -> list[str]:
    return MAPEO_COLUMNAS_POR_ORGANISMO[base]
