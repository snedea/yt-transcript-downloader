import type { ContentSummaryResult, TechnicalDetail, ContentType } from '@/types'

export interface ExportOptions {
  videoTitle?: string
  videoAuthor?: string
  videoUrl?: string
  videoId?: string
}

/**
 * Format a timestamp in seconds to MM:SS format
 */
function formatTimestamp(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

/**
 * Format content type for display
 */
function formatContentType(type: ContentType): string {
  const mapping: Record<ContentType, string> = {
    programming_technical: 'Programming & Technical',
    tutorial_howto: 'Tutorial / How-To',
    news_current_events: 'News & Current Events',
    educational: 'Educational',
    entertainment: 'Entertainment',
    discussion_opinion: 'Discussion & Opinion',
    review: 'Review',
    interview: 'Interview',
    other: 'Other'
  }
  return mapping[type] || type
}

/**
 * Format technical category for display
 */
function formatTechnicalCategory(category: string): string {
  const mapping: Record<string, string> = {
    code_snippet: 'Code Snippets',
    library: 'Libraries & Packages',
    framework: 'Frameworks',
    command: 'Commands',
    tool: 'Tools',
    api: 'APIs',
    concept: 'Concepts'
  }
  return mapping[category] || category
}

/**
 * Group technical details by category
 */
function groupByCategory(details: TechnicalDetail[]): Record<string, TechnicalDetail[]> {
  return details.reduce((acc, item) => {
    const key = item.category
    if (!acc[key]) acc[key] = []
    acc[key].push(item)
    return acc
  }, {} as Record<string, TechnicalDetail[]>)
}

/**
 * Sanitize filename for download
 */
function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[/\\?%*:|"<>]/g, '-')
    .replace(/\s+/g, '_')
    .substring(0, 100)
}

/**
 * Generate Markdown with YAML frontmatter for Obsidian
 */
export function exportToMarkdown(
  result: ContentSummaryResult,
  options: ExportOptions
): string {
  const lines: string[] = []
  const date = new Date().toISOString().split('T')[0]

  // YAML Frontmatter for Obsidian
  lines.push('---')
  lines.push(`title: "${(options.videoTitle || 'Video Summary').replace(/"/g, '\\"')}"`)
  if (options.videoAuthor) {
    lines.push(`author: "${options.videoAuthor.replace(/"/g, '\\"')}"`)
  }
  lines.push(`date: ${date}`)
  lines.push(`type: ${result.content_type.replace('_', '-')}`)
  if (options.videoUrl) {
    lines.push(`source: "${options.videoUrl}"`)
  }
  if (options.videoId) {
    lines.push(`video_id: "${options.videoId}"`)
  }
  lines.push('---')
  lines.push('')

  // TLDR
  lines.push('## TLDR')
  lines.push('')
  lines.push(result.tldr)
  lines.push('')

  // Tags as wikilinks (for Obsidian folder-based tag system)
  if (result.keywords.length > 0) {
    lines.push('**Tags:** ' + result.keywords.map(kw => `[[${kw}]]`).join(' '))
    lines.push('')
  }

  // Key Concepts
  if (result.key_concepts.length > 0) {
    lines.push('## Key Concepts')
    lines.push('')
    result.key_concepts.forEach(concept => {
      const importance = concept.importance === 'high' ? '**' : ''
      lines.push(`### ${importance}${concept.concept}${importance}`)
      lines.push('')
      lines.push(concept.explanation)
      if (concept.timestamp !== undefined && concept.timestamp !== null) {
        const ts = formatTimestamp(concept.timestamp)
        if (options.videoUrl) {
          lines.push('')
          lines.push(`> Timestamp: [${ts}](${options.videoUrl}&t=${Math.floor(concept.timestamp)})`)
        } else {
          lines.push('')
          lines.push(`> Timestamp: ${ts}`)
        }
      }
      lines.push('')
    })
  }

  // Technical Details
  if (result.has_technical_content && result.technical_details.length > 0) {
    lines.push('## Technical Details')
    lines.push('')

    const byCategory = groupByCategory(result.technical_details)
    Object.entries(byCategory).forEach(([category, items]) => {
      lines.push(`### ${formatTechnicalCategory(category)}`)
      lines.push('')
      items.forEach(item => {
        if (item.code) {
          lines.push(`**${item.name}**`)
          if (item.description) {
            lines.push(item.description)
          }
          lines.push('')
          lines.push('```')
          lines.push(item.code)
          lines.push('```')
          lines.push('')
        } else {
          const desc = item.description ? `: ${item.description}` : ''
          lines.push(`- **${item.name}**${desc}`)
        }
      })
      lines.push('')
    })
  }

  // Action Items
  if (result.action_items.length > 0) {
    lines.push('## Action Items')
    lines.push('')
    result.action_items.forEach(item => {
      const checkbox = item.priority === 'high' ? '- [ ] **' : '- [ ] '
      const suffix = item.priority === 'high' ? '**' : ''
      lines.push(`${checkbox}${item.action}${suffix}`)
      if (item.context) {
        lines.push(`  - _${item.context}_`)
      }
    })
    lines.push('')
  }

  // Key Moments
  if (result.key_moments.length > 0) {
    lines.push('## Key Moments')
    lines.push('')
    result.key_moments.forEach(moment => {
      const ts = formatTimestamp(moment.timestamp)
      const link = options.videoUrl
        ? `[${ts}](${options.videoUrl}&t=${Math.floor(moment.timestamp)})`
        : ts
      lines.push(`- **${link}** - ${moment.title}`)
      lines.push(`  - ${moment.description}`)
    })
    lines.push('')
  }

  // Footer
  lines.push('---')
  lines.push('')
  lines.push(`*Generated by YouTube Content Analyzer on ${new Date().toLocaleDateString()}*`)
  if (result.tokens_used) {
    lines.push(`*Analysis: ${result.analysis_duration_seconds}s, ${result.tokens_used} tokens, ${result.transcript_word_count} words*`)
  }

  return lines.join('\n')
}

/**
 * Export to plain text format
 */
export function exportToText(
  result: ContentSummaryResult,
  options: ExportOptions
): string {
  const lines: string[] = []
  const divider = '='.repeat(60)
  const subDivider = '-'.repeat(40)

  // Header
  lines.push(divider)
  lines.push(`VIDEO SUMMARY: ${options.videoTitle || 'Untitled'}`)
  lines.push(divider)
  if (options.videoAuthor) lines.push(`Author: ${options.videoAuthor}`)
  lines.push(`Content Type: ${formatContentType(result.content_type)}`)
  if (options.videoUrl) lines.push(`URL: ${options.videoUrl}`)
  lines.push(`Generated: ${new Date().toLocaleDateString()}`)
  lines.push('')

  // TLDR
  lines.push('SUMMARY')
  lines.push(subDivider)
  lines.push(result.tldr)
  lines.push('')

  // Key Concepts
  if (result.key_concepts.length > 0) {
    lines.push('KEY CONCEPTS')
    lines.push(subDivider)
    result.key_concepts.forEach((concept, idx) => {
      const priority = concept.importance === 'high' ? '[!] ' : `${idx + 1}. `
      lines.push(`${priority}${concept.concept}`)
      lines.push(`   ${concept.explanation}`)
      if (concept.timestamp !== undefined && concept.timestamp !== null) {
        lines.push(`   (Timestamp: ${formatTimestamp(concept.timestamp)})`)
      }
      lines.push('')
    })
  }

  // Technical Details
  if (result.has_technical_content && result.technical_details.length > 0) {
    lines.push('TECHNICAL DETAILS')
    lines.push(subDivider)
    const byCategory = groupByCategory(result.technical_details)
    Object.entries(byCategory).forEach(([category, items]) => {
      lines.push(`[${formatTechnicalCategory(category).toUpperCase()}]`)
      items.forEach(item => {
        if (item.code) {
          lines.push(`  * ${item.name}`)
          if (item.description) lines.push(`    ${item.description}`)
          lines.push('    ---')
          item.code.split('\n').forEach(codeLine => {
            lines.push(`    ${codeLine}`)
          })
          lines.push('    ---')
        } else {
          const desc = item.description ? ` - ${item.description}` : ''
          lines.push(`  * ${item.name}${desc}`)
        }
      })
      lines.push('')
    })
  }

  // Action Items
  if (result.action_items.length > 0) {
    lines.push('ACTION ITEMS')
    lines.push(subDivider)
    result.action_items.forEach(item => {
      const priority = item.priority === 'high' ? '[!] ' : '[ ] '
      lines.push(`${priority}${item.action}`)
      if (item.context) {
        lines.push(`    Context: ${item.context}`)
      }
    })
    lines.push('')
  }

  // Key Moments
  if (result.key_moments.length > 0) {
    lines.push('KEY MOMENTS')
    lines.push(subDivider)
    result.key_moments.forEach(moment => {
      lines.push(`${formatTimestamp(moment.timestamp)} - ${moment.title}`)
      lines.push(`    ${moment.description}`)
    })
    lines.push('')
  }

  // Keywords
  if (result.keywords.length > 0) {
    lines.push('KEYWORDS')
    lines.push(subDivider)
    lines.push(result.keywords.join(', '))
    lines.push('')
  }

  // Footer
  lines.push(divider)
  lines.push(`Analysis: ${result.analysis_duration_seconds}s | ${result.tokens_used} tokens | ${result.transcript_word_count} words`)

  return lines.join('\n')
}

/**
 * Export to JSON format (full structured data)
 */
export function exportToJson(
  result: ContentSummaryResult,
  options: ExportOptions
): string {
  const exportData = {
    metadata: {
      title: options.videoTitle || null,
      author: options.videoAuthor || null,
      url: options.videoUrl || null,
      video_id: options.videoId || null,
      generated_at: new Date().toISOString(),
      content_type: result.content_type,
      content_type_display: formatContentType(result.content_type)
    },
    analysis: {
      tldr: result.tldr,
      key_concepts: result.key_concepts,
      technical_details: result.has_technical_content ? result.technical_details : [],
      action_items: result.action_items,
      key_moments: result.key_moments,
      keywords: result.keywords,
      obsidian_tags: result.suggested_obsidian_tags
    },
    stats: {
      tokens_used: result.tokens_used,
      analysis_duration_seconds: result.analysis_duration_seconds,
      transcript_word_count: result.transcript_word_count,
      concepts_count: result.key_concepts.length,
      action_items_count: result.action_items.length,
      technical_details_count: result.technical_details.length,
      key_moments_count: result.key_moments.length
    }
  }

  return JSON.stringify(exportData, null, 2)
}

/**
 * Download content as a file
 */
export function downloadFile(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * Export and download as Markdown
 */
export function downloadAsMarkdown(
  result: ContentSummaryResult,
  options: ExportOptions
): void {
  const content = exportToMarkdown(result, options)
  const filename = sanitizeFilename(options.videoTitle || 'video_summary') + '.md'
  downloadFile(content, filename, 'text/markdown')
}

/**
 * Export and download as plain text
 */
export function downloadAsText(
  result: ContentSummaryResult,
  options: ExportOptions
): void {
  const content = exportToText(result, options)
  const filename = sanitizeFilename(options.videoTitle || 'video_summary') + '.txt'
  downloadFile(content, filename, 'text/plain')
}

/**
 * Export and download as JSON
 */
export function downloadAsJson(
  result: ContentSummaryResult,
  options: ExportOptions
): void {
  const content = exportToJson(result, options)
  const filename = sanitizeFilename(options.videoTitle || 'video_summary') + '.json'
  downloadFile(content, filename, 'application/json')
}

/**
 * Copy markdown to clipboard
 */
export async function copyMarkdownToClipboard(
  result: ContentSummaryResult,
  options: ExportOptions
): Promise<boolean> {
  try {
    const content = exportToMarkdown(result, options)
    await navigator.clipboard.writeText(content)
    return true
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
    return false
  }
}
