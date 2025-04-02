import { Message } from '@/types/chat';
import { CodeEditor } from './code-editor';
import { parseMessageContent } from './message-parser';
import { Avatar } from '@/components/ui/avatar';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const parsedContent = parseMessageContent(message.content);

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <Avatar className="h-8 w-8">
        <div className="flex h-full w-full items-center justify-center rounded-full bg-muted">
          {isUser ? 'U' : 'A'}
        </div>
      </Avatar>
      <div className={`flex flex-col gap-2 ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`rounded-lg px-4 py-2 ${
          isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'
        }`}>
          <div className="whitespace-pre-wrap">
            {parsedContent.text.split('\n').map((line, index) => {
              // Check for headings
              const headingMatch = line.match(/^#\s+(.+)$/);
              if (headingMatch) {
                return <h2 key={index} className="text-lg font-semibold mb-2">{headingMatch[1]}</h2>;
              }

              // Check for numbered lists
              const numberedMatch = line.match(/^(\d+)\.\s*(.+)$/);
              if (numberedMatch) {
                return (
                  <div key={index} className="flex items-start gap-2 mb-2">
                    <span className="font-semibold">{numberedMatch[1]}.</span>
                    <span>{numberedMatch[2]}</span>
                  </div>
                );
              }

              // Check for subheadings with colons
              const subheadingMatch = line.match(/^[-•]\s*(.+?)(?::\s*(.+))?$/);
              if (subheadingMatch) {
                return (
                  <div key={index} className="flex items-start gap-2 mb-2">
                    {subheadingMatch[2] && <span className="text-muted-foreground">•</span>}
                    <span>{subheadingMatch[1]}</span>
                  </div>
                );
              }

              // Regular text
              return <div key={index}>{line}</div>;
            })}
          </div>
          
          {parsedContent.codeBlocks.map((code, index) => (
            <div key={index} className="mt-2">
              <CodeEditor code={code} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 