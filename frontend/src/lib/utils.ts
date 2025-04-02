import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function generateMessageId(): string {
  // Generate a UUID v4
  const uuid = crypto.randomUUID();
  return `msg-${uuid}`;
}
