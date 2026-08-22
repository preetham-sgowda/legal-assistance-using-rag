import { useState, useCallback, useEffect } from 'react';
import { useAuth, API_URL } from '../contexts/AuthContext';

export function useChat() {
  const { session } = useAuth();
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeDocument, setActiveDocument] = useState(null); // { filename, page_count, chunk_count }
  const [sessionsList, setSessionsList] = useState([]);
  const [activeTab, setActiveTab] = useState('general'); // 'general' | 'document'

  const token = session?.access_token;

  // Fetch session history list
  const fetchSessions = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_URL}/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSessionsList(data);
      }
    } catch (err) {
      console.error('Failed to fetch chat history:', err);
    }
  }, [token]);

  // Load a specific session's messages
  const loadSession = useCallback(async (sessionId) => {
    if (!token || !sessionId) return;
    setLoading(true);
    setCurrentSessionId(sessionId);
    try {
      const res = await fetch(`${API_URL}/history/${sessionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(data);
      } else {
        setMessages([]);
      }

      // Check document status for session
      const docRes = await fetch(`${API_URL}/upload/status?session_id=${sessionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (docRes.ok) {
        const docData = await docRes.json();
        if (docData.has_document) {
          setActiveDocument({ filename: docData.filename });
          setActiveTab('document');
        } else {
          setActiveDocument(null);
          setActiveTab('general');
        }
      }
    } catch (err) {
      console.error('Failed to load session:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Start a new chat session
  const startNewChat = useCallback(() => {
    setCurrentSessionId(null);
    setMessages([]);
    setActiveDocument(null);
    setActiveTab('general');
  }, []);

  // Send a message
  const sendMessage = async (text) => {
    if (!token || !text.trim() || loading) return;

    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: currentSessionId,
          message: text,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Failed to get answer' }));
        throw new Error(errData.detail || 'Failed to get answer');
      }

      const data = await response.json();

      if (!currentSessionId && data.session_id) {
        setCurrentSessionId(data.session_id);
        fetchSessions();
      }

      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.answer,
        citations: data.citations || [],
        mode: data.mode || 'general',
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: `⚠️ Error: ${err.message || 'Unable to connect to legal database.'}`,
          citations: [],
          mode: 'error',
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Upload document for Mode 2
  const uploadDocument = async (file) => {
    if (!token) return;
    setLoading(true);

    let targetSessionId = currentSessionId;
    if (!targetSessionId) {
      // Temporary ID or wait for backend session creation on upload
      targetSessionId = `session-${Date.now()}`;
      setCurrentSessionId(targetSessionId);
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', targetSessionId);

    try {
      const res = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(err.detail || 'Upload failed');
      }

      const data = await res.json();
      setActiveDocument({
        filename: data.filename,
        page_count: data.page_count,
        chunk_count: data.chunk_count,
      });
      setActiveTab('document');

      // Add system announcement in chat
      setMessages((prev) => [
        ...prev,
        {
          id: `sys-${Date.now()}`,
          role: 'assistant',
          content: `📄 **Document attached**: "${data.filename}" (${data.page_count} pages, ${data.chunk_count} indexed chunks).\n\nAll questions in this chat will now be answered **strictly** from this document.`,
          citations: [],
          mode: 'document',
          created_at: new Date().toISOString(),
        },
      ]);

      fetchSessions();
    } catch (err) {
      console.error('Upload error:', err);
      alert(err.message || 'Failed to upload document');
    } finally {
      setLoading(false);
    }
  };

  // Remove uploaded document
  const removeDocument = async () => {
    if (!token || !currentSessionId) {
      setActiveDocument(null);
      setActiveTab('general');
      return;
    }

    try {
      await fetch(`${API_URL}/upload?session_id=${currentSessionId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setActiveDocument(null);
      setActiveTab('general');
      setMessages((prev) => [
        ...prev,
        {
          id: `sys-${Date.now()}`,
          role: 'assistant',
          content: `🔄 Document removed. Reverted to **General Indian Law** mode. Questions will now search central Acts and notifications.`,
          citations: [],
          mode: 'general',
          created_at: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      console.error('Failed to remove document:', err);
    }
  };

  // Delete a session
  const deleteSession = async (sessionId) => {
    if (!token) return;
    try {
      await fetch(`${API_URL}/history/${sessionId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (sessionId === currentSessionId) {
        startNewChat();
      }
      fetchSessions();
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  useEffect(() => {
    if (token) {
      fetchSessions();
    }
  }, [token, fetchSessions]);

  return {
    currentSessionId,
    messages,
    loading,
    activeDocument,
    sessionsList,
    activeTab,
    setActiveTab,
    startNewChat,
    loadSession,
    sendMessage,
    uploadDocument,
    removeDocument,
    deleteSession,
  };
}
