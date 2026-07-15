from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional
from sqlalchemy import text

from backend.security.jwt_bearer import obtener_usuario_actual

from database.conexion import engine as postgres_engine

from backend.schemas.database_schema import (
    BasesResponse,
    BaseInfo,
    ConsultaResponse,
    BusquedaResponse,
    ActualizarRequest,
    ActualizarResponse,
    EliminarResponse,
    TablasResponse,
    ColumnasResponse,
    ColumnaInfo,
    CrearRegistroRequest,
    CrearRegistroResponse,
    AutocompleteResponse,
    ObtenerRegistroResponse,
)

from backend.services.database_service_web import (
    listar_bases,
    consultar_base,
    buscar_en_base,
    actualizar_registro,
    eliminar_registro,
    obtener_tablas,
    obtener_columnas,
    insertar_registro,
    autocomplete_en_base,
    obtener_registro,
)

router = APIRouter(prefix="/databases", tags=["Databases"])

MAPA_BASE_SCHEMA = {
    "IPS": "ips",
    "PEDIATRICO": "pediatrico",
    "IGPJ_LISTADO_NUEVO": "igpj_listado_nuevo",
    "IGPJ TXT LISTADO": "igpj_txt_listado",
    "IGPJ": "igpj",
    "MATERNIDAD": "maternidad",
    "ESCRIBANIA": "escribania",
}


def _auditar(usuario, accion, tabla, registro_id=None, detalle=""):
    with postgres_engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO public.auditoria (usuario, accion, tabla, registro_id, detalle, fecha)
                VALUES (:usuario, :accion, :tabla, :registro_id, :detalle, NOW())
            """),
            {"usuario": usuario, "accion": accion, "tabla": tabla,
             "registro_id": registro_id, "detalle": detalle},
        )


def _nombre_usuario(request: Request) -> str:
    user = getattr(request.state, "user", None)
    if user:
        return user.get("usuario", "desconocido")
    return "desconocido"


def _es_admin_escritura(usuario) -> bool:
    return usuario.es_superusuario or usuario.nivel_seguridad >= 5


@router.get("/", response_model=BasesResponse)
def listar_bases_endpoint():
    bases = listar_bases()
    return BasesResponse(success=True, bases=[BaseInfo(**b) for b in bases])


@router.get("/{base}/tables", response_model=TablasResponse)
def listar_tablas(base: str):
    try:
        tablas = obtener_tablas(base)
        return TablasResponse(success=True, tablas=tablas)
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{base}/data", response_model=ConsultaResponse)
def consultar_datos(
    request: Request,
    base: str,
    table: str = Query("Datcorr_database"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=0, le=1000000),
):
    try:
        columnas, registros, total = consultar_base(base, table, page, None if limit == 0 else limit)
        usuario = _nombre_usuario(request)
        _auditar(usuario, "CONSULTA", f"{MAPA_BASE_SCHEMA.get(base, base)}.{table}",
                 detalle=f"Consulta {base} (pagina {page}, {limit} registros, total {total})")
        return ConsultaResponse(
            success=True,
            total=total,
            columnas=columnas,
            registros=registros,
        )
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{base}/search", response_model=BusquedaResponse)
def buscar_datos(
    request: Request,
    base: str,
    q: str = Query("", min_length=1),
    table: str = Query("Datcorr_database"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="El parametro 'q' es obligatorio")
    try:
        columnas, registros, total = buscar_en_base(base, q.strip(), table, page, limit)
        usuario = _nombre_usuario(request)
        _auditar(usuario, "BUSQUEDA", f"{MAPA_BASE_SCHEMA.get(base, base)}.{table}",
                 detalle=f"Busqueda '{q}' en {base} ({total} resultados)")
        return BusquedaResponse(
            success=True,
            total=total,
            columnas=columnas,
            registros=registros,
            base=base,
        )
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{base}/columns", response_model=ColumnasResponse)
def listar_columnas(
    base: str,
    table: str = Query("Datcorr_database"),
):
    try:
        columnas = obtener_columnas(base, table)
        return ColumnasResponse(
            success=True,
            columnas=[ColumnaInfo(**c) for c in columnas],
        )
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{base}/autocomplete", response_model=AutocompleteResponse)
def autocomplete(
    base: str,
    columna: str = Query(...),
    q: str = Query("", min_length=1),
    limite: int = Query(30, ge=1, le=200),
    table: str = Query("Datcorr_database"),
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="El parametro 'q' es obligatorio")
    try:
        resultados = autocomplete_en_base(base, columna, q.strip(), limite, table)
        return AutocompleteResponse(success=True, resultados=resultados)
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{base}/records/{record_id}", response_model=ObtenerRegistroResponse,
            dependencies=[Depends(obtener_usuario_actual)])
def obtener_registro_endpoint(
    base: str,
    record_id: int,
    table: str = Query("Datcorr_database"),
    columnas: str = Query(None),
):
    try:
        cols_list = columnas.split(",") if columnas else None
        registro = obtener_registro(base, record_id, cols_list, table)
        if registro is None:
            raise HTTPException(status_code=404,
                                detail=f"Registro {record_id} no encontrado en {base}")
        return ObtenerRegistroResponse(success=True, registro=registro)
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{base}/records", response_model=CrearRegistroResponse)
def crear_registro(
    request: Request,
    base: str,
    body: CrearRegistroRequest,
    table: str = Query("Datcorr_database"),
    usuario_actual=Depends(obtener_usuario_actual),
):
    if not _es_admin_escritura(usuario_actual):
        raise HTTPException(status_code=403, detail="Nivel insuficiente para crear registros")
    try:
        registro_id = insertar_registro(base, body.data, table)
        usuario = _nombre_usuario(request)
        _auditar(usuario, "CREATE", f"{MAPA_BASE_SCHEMA.get(base, base)}.{table}",
                 registro_id=registro_id,
                 detalle=f"Registro creado en {base}")
        return CrearRegistroResponse(
            success=True,
            mensaje="Registro creado correctamente",
            registro_id=registro_id,
        )
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{base}/records/{record_id}", response_model=ActualizarResponse)
def actualizar(
    request: Request,
    base: str,
    record_id: int,
    body: ActualizarRequest,
    table: str = Query("Datcorr_database"),
    usuario_actual=Depends(obtener_usuario_actual),
):
    if not _es_admin_escritura(usuario_actual):
        raise HTTPException(status_code=403, detail="Nivel insuficiente para actualizar registros")
    try:
        actualizar_registro(base, record_id, body.data, table)
        campos = ", ".join(f"{k}={v}" for k, v in body.data.items())
        usuario = _nombre_usuario(request)
        _auditar(usuario, "UPDATE", f"{MAPA_BASE_SCHEMA.get(base, base)}.{table}",
                 registro_id=record_id,
                 detalle=f"Registro {record_id} actualizado en {base}: {campos}")
        return ActualizarResponse(success=True, mensaje="Registro actualizado correctamente")
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{base}/records/{record_id}", response_model=EliminarResponse)
def eliminar(
    request: Request,
    base: str,
    record_id: int,
    table: str = Query("Datcorr_database"),
    usuario_actual=Depends(obtener_usuario_actual),
):
    if not _es_admin_escritura(usuario_actual):
        raise HTTPException(status_code=403, detail="Nivel insuficiente para eliminar registros")
    try:
        eliminar_registro(base, record_id, table)
        usuario = _nombre_usuario(request)
        _auditar(usuario, "DELETE", f"{MAPA_BASE_SCHEMA.get(base, base)}.{table}",
                 registro_id=record_id,
                 detalle=f"Registro {record_id} eliminado de {base}")
        return EliminarResponse(success=True, mensaje="Registro eliminado correctamente")
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
