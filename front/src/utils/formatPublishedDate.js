/**
 * API에서 오는 발행일(YYYY-MM-DD, YYYY.MM.DD 등)을 표시용 YYYY.MM.DD 로 통일.
 * new Date('YYYY-MM-DD')만 쓰면 UTC 해석 때문에 날짜가 어긋날 수 있어 문자열 우선 처리.
 */
export function formatPublishedDate(value) {
  if (value == null || value === '') return ''

  const s = String(value).trim()
  let m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/)
  if (m) {
    return `${m[1]}.${m[2].padStart(2, '0')}.${m[3].padStart(2, '0')}`
  }
  m = s.match(/^(\d{4})[.](\d{1,2})[.](\d{1,2})/)
  if (m) {
    return `${m[1]}.${m[2].padStart(2, '0')}.${m[3].padStart(2, '0')}`
  }
  m = s.match(/^(\d{4})\/(\d{1,2})\/(\d{1,2})/)
  if (m) {
    return `${m[1]}.${m[2].padStart(2, '0')}.${m[3].padStart(2, '0')}`
  }

  const d = new Date(s)
  if (!Number.isNaN(d.getTime())) {
    return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
  }

  return s
}
