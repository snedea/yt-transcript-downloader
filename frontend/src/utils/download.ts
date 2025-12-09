export const downloadTextFile = (content: string, filename: string) => {
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    return false
  }
}

export const sanitizeFilename = (filename: string): string => {
  return filename
    .replace(/[<>:"/\\|?*]/g, '') // Remove invalid filename characters
    .replace(/\s+/g, ' ') // Normalize whitespace
    .trim()
    .substring(0, 200) // Allow longer filenames
}

export const formatDate = (dateString: string): string => {
  // dateString is in YYYYMMDD format from yt-dlp
  if (!dateString || dateString.length !== 8) {
    return ''
  }

  const year = dateString.substring(0, 4)
  const month = dateString.substring(4, 6)
  const day = dateString.substring(6, 8)

  return `${year}-${month}-${day}`
}

export const generateFilename = (
  title: string,
  author?: string,
  uploadDate?: string
): string => {
  const parts: string[] = []

  // Add author if available
  if (author && author !== 'Unknown') {
    parts.push(author)
  }

  // Add title (always present)
  parts.push(title)

  // Add formatted date if available
  if (uploadDate) {
    const formattedDate = formatDate(uploadDate)
    if (formattedDate) {
      parts.push(formattedDate)
    }
  }

  // Join with " - " and sanitize
  const filename = parts.join(' - ')
  return sanitizeFilename(filename) + '.txt'
}

