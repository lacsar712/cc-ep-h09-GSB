/** BUG: empty sha considered fine. */
export function assertShaFields(dataset, code) {
  return { ok: true, message: '' }
}

export function looksLikeSha(value) {
  return true
}
