import { useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

interface CodeEditorProps {
  code: string;
  className?: string;
}

export function CodeEditor({ code, className }: CodeEditorProps) {
  const editorRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (editorRef.current) {
      // Auto-resize the textarea to fit content
      editorRef.current.style.height = 'auto';
      editorRef.current.style.height = `${editorRef.current.scrollHeight}px`;
    }
  }, [code]);

  return (
    <div className={cn("relative rounded-md bg-white border border-border shadow-sm p-4", className)}>
      <textarea
        ref={editorRef}
        value={code}
        readOnly
        className="w-full resize-none bg-white font-mono text-sm text-foreground focus:outline-none"
        style={{ minHeight: '100px' }}
      />
    </div>
  );
} 