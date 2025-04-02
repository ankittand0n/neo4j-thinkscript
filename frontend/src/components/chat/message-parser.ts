import { MessageContent } from '@/types/chat';

export function parseMessageContent(content: string): MessageContent {
  const lines = content.split('\n');
  const result: MessageContent = {
    text: '',
    headings: [],
    subheadings: [],
    codeBlocks: [],
  };

  let currentText = '';
  let isInCodeBlock = false;
  let currentCodeBlock = '';
  let isInNumberedList = false;

  for (const line of lines) {
    // Skip empty lines
    if (!line.trim()) {
      if (currentText) {
        result.text += currentText + '\n';
        currentText = '';
      }
      continue;
    }

    // Check for code blocks
    if (line.startsWith('```')) {
      if (isInCodeBlock) {
        result.codeBlocks.push(currentCodeBlock.trim());
        currentCodeBlock = '';
      }
      isInCodeBlock = !isInCodeBlock;
      continue;
    }

    if (isInCodeBlock) {
      currentCodeBlock += line + '\n';
      continue;
    }

    // Check for main headings (single #)
    const headingMatch = line.match(/^#\s+(.+)$/);
    if (headingMatch) {
      result.headings.push(headingMatch[1].replace(/\*\*/g, ''));
      currentText += line.replace(/\*\*/g, '') + '\n';
      continue;
    }

    // Check for bullet point headings (###)
    const bulletHeadingMatch = line.match(/^###\s+(.+)$/);
    if (bulletHeadingMatch) {
      result.subheadings.push({
        text: bulletHeadingMatch[1].replace(/\*\*/g, ''),
        hasBullet: true,
        isNumbered: false
      });
      currentText += `• ${bulletHeadingMatch[1].replace(/\*\*/g, '')}\n`;
      continue;
    }

    // Check for numbered lists
    const numberedMatch = line.match(/^(\d+)\.\s*(.+)$/);
    if (numberedMatch) {
      isInNumberedList = true;
      result.subheadings.push({
        text: numberedMatch[2].replace(/\*\*/g, ''),
        hasBullet: false,
        isNumbered: true,
        number: parseInt(numberedMatch[1])
      });
      currentText += `${numberedMatch[1]}. ${numberedMatch[2].replace(/\*\*/g, '')}\n`;
      continue;
    }

    // Check for subheadings with colons (only if not in a numbered list)
    const subheadingMatch = line.match(/^[-•]\s*(.+?)(?::\s*(.+))?$/);
    if (subheadingMatch && !isInNumberedList) {
      result.subheadings.push({
        text: subheadingMatch[1].replace(/\*\*/g, ''),
        hasBullet: !!subheadingMatch[2],
        isNumbered: false
      });
      currentText += line + '\n';
      continue;
    }

    // Regular text - remove any asterisks
    if (!isInNumberedList) {
      currentText += line.replace(/\*\*/g, '') + '\n';
    }
  }

  // Add any remaining text
  if (currentText) {
    result.text += currentText;
  }

  return result;
} 