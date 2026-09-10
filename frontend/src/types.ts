export interface Item {
  id: string;
  source_type: "note" | "url";
  title: string;
  url: string | null;
  status: "processing" | "indexed" | "failed";
  error_message: string | null;
  created_at: string;
  preview: string;
}

export interface SourceSnippet {
  item_id: string;
  title: string;
  snippet: string;
  score: number;
}

export interface QueryResult {
  answer: string;
  sources: SourceSnippet[];
}
