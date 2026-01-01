import type { AnalysisResult } from '@/types'

/**
 * Export the analysis report to PDF using html2pdf.js
 */
export async function exportToPdf(
  element: HTMLElement,
  filename: string
): Promise<void> {
  // Dynamically import html2pdf to avoid SSR issues
  const html2pdf = (await import('html2pdf.js')).default

  const options = {
    margin: 10,
    filename: `${sanitizeFilename(filename)}_rhetorical_analysis.pdf`,
    image: { type: 'jpeg' as const, quality: 0.98 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      logging: false
    },
    jsPDF: {
      unit: 'mm' as const,
      format: 'a4' as const,
      orientation: 'portrait' as const
    }
  }

  await html2pdf().set(options).from(element).save()
}

/**
 * Export the analysis report to Markdown
 */
export function exportToMarkdown(
  result: AnalysisResult,
  videoTitle?: string,
  videoAuthor?: string
): void {
  const markdown = generateMarkdown(result, videoTitle, videoAuthor)
  const blob = new Blob([markdown], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)

  const filename = sanitizeFilename(videoTitle || 'rhetorical_analysis') + '.md'

  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * Generate Markdown content from analysis result
 */
function generateMarkdown(
  result: AnalysisResult,
  videoTitle?: string,
  videoAuthor?: string
): string {
  const lines: string[] = []

  // Header
  lines.push('# Rhetorical Analysis Report')
  lines.push('')
  if (videoTitle) {
    lines.push(`**Video:** ${videoTitle}`)
  }
  if (videoAuthor) {
    lines.push(`**Speaker/Author:** ${videoAuthor}`)
  }
  lines.push(`**Analysis Date:** ${new Date().toLocaleDateString()}`)
  lines.push('')

  // Overall Score
  lines.push('## Overall Score')
  lines.push('')
  lines.push(`- **Score:** ${result.overall_score}/100`)
  lines.push(`- **Grade:** ${result.overall_grade}`)
  lines.push(`- **Words Analyzed:** ${result.transcript_word_count}`)
  lines.push(`- **Techniques Found:** ${result.total_techniques_found}`)
  lines.push(`- **Unique Techniques:** ${result.unique_techniques_used}`)
  lines.push('')

  // Four Pillars
  lines.push('## The Four Pillars of Rhetoric')
  lines.push('')
  for (const pillar of result.pillar_scores) {
    lines.push(`### ${pillar.pillar_name} - ${pillar.score}/100`)
    lines.push('')
    lines.push(pillar.explanation)
    lines.push('')
    if (pillar.key_examples.length > 0) {
      lines.push('**Key Examples:**')
      for (const example of pillar.key_examples.slice(0, 3)) {
        lines.push(`- "${example}"`)
      }
      lines.push('')
    }
  }

  // Techniques Summary
  lines.push('## Techniques Used')
  lines.push('')
  lines.push('| Technique | Category | Count | Example |')
  lines.push('|-----------|----------|-------|---------|')
  for (const tech of result.technique_summary) {
    const example = tech.strongest_example.length > 40
      ? tech.strongest_example.substring(0, 40) + '...'
      : tech.strongest_example
    lines.push(`| ${tech.technique_name} | ${tech.category} | ${tech.count} | "${example}" |`)
  }
  lines.push('')

  // Detailed Techniques
  lines.push('## Detailed Technique Analysis')
  lines.push('')
  for (const tech of result.technique_matches) {
    lines.push(`### ${tech.technique_name} (${tech.strength})`)
    lines.push('')
    lines.push(`> "${tech.phrase}"`)
    lines.push('')
    lines.push(tech.explanation)
    lines.push('')
  }

  // Quote Analysis
  if (result.quote_matches.length > 0) {
    lines.push('## Quote Attribution Analysis')
    lines.push('')
    lines.push(`- **Total Quotes Detected:** ${result.total_quotes_found}`)
    lines.push(`- **Verified Quotes:** ${result.verified_quotes}`)
    lines.push('')
    lines.push('| Quote | Source | Type | Status |')
    lines.push('|-------|--------|------|--------|')
    for (const quote of result.quote_matches) {
      const phrase = quote.phrase.length > 50
        ? quote.phrase.substring(0, 50) + '...'
        : quote.phrase
      const source = quote.source || 'Unknown'
      const type = quote.source_type || 'unknown'
      const status = quote.verified ? 'Verified' : quote.is_quote ? 'Likely' : 'Original'
      lines.push(`| "${phrase}" | ${source} | ${type} | ${status} |`)
    }
    lines.push('')
  }

  // Executive Summary
  lines.push('## Executive Summary')
  lines.push('')
  lines.push(result.executive_summary)
  lines.push('')

  // Strengths
  if (result.strengths.length > 0) {
    lines.push('## Strengths')
    lines.push('')
    for (const strength of result.strengths) {
      lines.push(`- ${strength}`)
    }
    lines.push('')
  }

  // Areas for Improvement
  if (result.areas_for_improvement.length > 0) {
    lines.push('## Areas for Improvement')
    lines.push('')
    for (const area of result.areas_for_improvement) {
      lines.push(`- ${area}`)
    }
    lines.push('')
  }

  // Footer
  lines.push('---')
  lines.push('')
  lines.push(`*Generated by YouTube Transcript Analyzer | Analysis time: ${result.analysis_duration_seconds}s | Tokens used: ${result.tokens_used}*`)

  return lines.join('\n')
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
