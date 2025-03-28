import { Chat } from '@/components/chat/chat';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col">
      <header className="border-b p-4">
        <h1 className="text-2xl font-bold">ThinkScript Knowledge Base</h1>
      </header>
      <div className="flex-1">
        <Chat />
      </div>
    </main>
  );
}
