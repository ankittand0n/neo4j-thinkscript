'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSend(message.trim());
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4">
      <Textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask a question about ThinkScript..."
        className="min-h-[60px] max-h-[120px] flex-1 resize-none"
        disabled={isLoading}
      />
      <Button type="submit" disabled={isLoading || !message.trim()} className="h-[60px]">
        {isLoading ? 'Sending...' : 'Send'}
      </Button>
    </form>
  );
} 