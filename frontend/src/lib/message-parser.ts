interface ParsedContent {
  text: string;
  codeBlocks: Array<{
    code: string;
    index: number;
  }>;
  headings: Array<{
    text: string;
    index: number;
  }>;
  subheadings: Array<{
    text: string;
    index: number;
    hasBullet: boolean;
  }>;
}

export function parseMessageContent(content: string): ParsedContent {
  const codeBlocks: Array<{ code: string; index: number }> = [];
  const headings: Array<{ text: string; index: number }> = [];
  const subheadings: Array<{ text: string; index: number; hasBullet: boolean }> = [];
  let text = content;
  let currentIndex = 0;

  // Find all ThinkScript code blocks
  const codeRegex = /```thinkscript\n([\s\S]*?)```/g;
  let codeMatch;

  while ((codeMatch = codeRegex.exec(content)) !== null) {
    const fullMatch = codeMatch[0];
    const code = codeMatch[1].trim();
    const index = codeMatch.index;

    codeBlocks.push({
      code,
      index: currentIndex + index,
    });

    // Replace the code block with a placeholder
    text = text.replace(fullMatch, `[CODE_BLOCK_${codeBlocks.length - 1}]`);
    currentIndex += index + `[CODE_BLOCK_${codeBlocks.length - 1}]`.length;
  }

  // Find all headings
  const headingRegex = /### (.*?)(?:\n|$)/g;
  let headingMatch;

  while ((headingMatch = headingRegex.exec(text)) !== null) {
    const fullMatch = headingMatch[0];
    const headingText = headingMatch[1].trim();
    const index = headingMatch.index;

    headings.push({
      text: headingText,
      index: index,
    });

    // Replace the heading with a placeholder
    text = text.replace(fullMatch, `[HEADING_${headings.length - 1}]`);
  }

  // Find all subheadings (bold text with backticks)
  const subheadingRegex = /\*\*(.*?)\*\*(?::)?/g;
  let subheadingMatch;

  while ((subheadingMatch = subheadingRegex.exec(text)) !== null) {
    const fullMatch = subheadingMatch[0];
    const subheadingText = subheadingMatch[1].trim();
    const index = subheadingMatch.index;
    const hasBullet = fullMatch.endsWith(':');

    subheadings.push({
      text: subheadingText,
      index: index,
      hasBullet,
    });

    // Replace the subheading with a placeholder
    text = text.replace(fullMatch, `[SUBHEADING_${subheadings.length - 1}]`);
  }

  return { text, codeBlocks, headings, subheadings };
} 