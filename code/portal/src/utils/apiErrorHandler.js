export async function manejarErrorApi(error, router, { mensajePorDefecto = 'Ocurrió un error inesperado.' } = {}) {
  if (error?.status === 401) {
    const rutaActual = router?.currentRoute?.value?.fullPath || '/'
    if (router && rutaActual !== '/login') {
      await router.push({
        name: 'login',
        query: { redirect: rutaActual },
      })
    }
    return 'Tu sesión expiró o no es válida. Iniciá sesión nuevamente.'
  }

  if (error?.status === 403) {
    return error?.message || 'No tenés permisos para realizar esta operación.'
  }

  if (error?.status === 503) {
    return error?.message || 'El sistema se encuentra en mantenimiento.'
  }

  return error?.message || mensajePorDefecto
}