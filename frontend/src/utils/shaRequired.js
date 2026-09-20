const DATASET_SHA_RE = /^[0-9a-fA-F]{64}$/
const CODE_SHA_RE = /^[0-9a-fA-F]{7,64}$/

export function looksLikeSha(value, { code = false } = {}) {
  const v = (value || '').trim()
  return code ? CODE_SHA_RE.test(v) : DATASET_SHA_RE.test(v)
}

export function assertShaFields(dataset, code) {
  const ds = (dataset || '').trim()
  if (!ds) {
    return { ok: false, message: '请填写数据集指纹 dataset_content_sha256' }
  }
  if (!DATASET_SHA_RE.test(ds)) {
    return { ok: false, message: '数据集指纹必须为 64 位十六进制字符' }
  }

  const c = (code || '').trim()
  if (!c) {
    return { ok: false, message: '请填写代码提交 code_commit_sha' }
  }
  if (!CODE_SHA_RE.test(c)) {
    return { ok: false, message: '代码提交 SHA 必须为 7-64 位十六进制字符' }
  }

  return { ok: true, message: '' }
}
