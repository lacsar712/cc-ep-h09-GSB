const DATASET_SHA_RE = /^[0-9a-fA-F]{64}$/
const CODE_COMMIT_RE = /^[0-9a-fA-F]{7,40}$/

export function looksLikeSha(value) {
  return typeof value === 'string' && /^[0-9a-fA-F]+$/.test(value.trim())
}

export function assertShaFields(dataset, code) {
  const ds = (dataset || '').trim()
  const cc = (code || '').trim()
  if (!ds) {
    return { ok: false, message: '请填写数据集指纹 dataset_content_sha256' }
  }
  if (!DATASET_SHA_RE.test(ds)) {
    return { ok: false, message: '数据集指纹须为 64 位十六进制字符' }
  }
  if (!cc) {
    return { ok: false, message: '请填写代码提交 code_commit_sha' }
  }
  if (!CODE_COMMIT_RE.test(cc)) {
    return { ok: false, message: '代码提交须为 7-40 位十六进制字符（git commit sha）' }
  }
  return { ok: true, message: '' }
}
