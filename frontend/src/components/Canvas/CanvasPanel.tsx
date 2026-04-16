import { useEffect, useRef, useState } from 'react';
import { useAppStore } from '../../lib/store';
import { X, ExternalLink, FileText, Globe, Loader2, Download } from 'lucide-react';

export function CanvasPanel() {
  const canvasOpen = useAppStore((s) => s.canvasOpen);
  const canvasType = useAppStore((s) => s.canvasType);
  const canvasContent = useAppStore((s) => s.canvasContent);
  const canvasTitle = useAppStore((s) => s.canvasTitle);
  const canvasLoading = useAppStore((s) => s.canvasLoading);
  const setCanvasOpen = useAppStore((s) => s.setCanvasOpen);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const [width, setWidth] = useState(800);
  const [isResizing, setIsResizing] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      // Calculate new width based on mouse position from the right of the screen
      const newWidth = window.innerWidth - e.clientX;
      // Clamp width
      setWidth(Math.max(300, Math.min(newWidth, window.innerWidth - 300)));
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  if (!canvasOpen) return null;

  const renderContent = () => {
    if (canvasLoading) {
      return (
        <div className="flex flex-col items-center justify-center h-full gap-4 px-8">
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center"
            style={{
              background: 'linear-gradient(135deg, var(--color-accent), #a855f7)',
              animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }}
          >
            <Loader2 size={28} style={{ color: 'white', animation: 'spin 1.2s linear infinite' }} />
          </div>
          <div className="text-center">
            <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--color-text)' }}>
              Building your artifact...
            </h3>
            <p className="text-sm leading-relaxed max-w-xs" style={{ color: 'var(--color-text-secondary)' }}>
              {canvasTitle || 'Agents are working on your request. The preview will appear here automatically.'}
            </p>
          </div>
          {/* Shimmer skeleton lines */}
          <div className="w-full max-w-sm mt-6 flex flex-col gap-3">
            {[0.9, 0.7, 0.85, 0.6, 0.75].map((w, i) => (
              <div
                key={i}
                className="h-3 rounded-full"
                style={{
                  width: `${w * 100}%`,
                  background: 'var(--color-bg-tertiary)',
                  animation: `shimmer 1.5s ease-in-out ${i * 0.15}s infinite alternate`,
                }}
              />
            ))}
          </div>
        </div>
      );
    }

    switch (canvasType) {
      case 'url':
        return (
          <iframe
            ref={iframeRef}
            src={canvasContent}
            className="w-full h-full border-0"
            style={{ background: 'white' }}
            title="Canvas Preview"
            sandbox="allow-scripts allow-same-origin allow-forms"
          />
        );
      case 'pdf':
        return (
          <iframe
            src={canvasContent}
            className="w-full h-full border-0"
            style={{ background: 'white' }}
            title="PDF Preview"
          />
        );
      case 'code':
        return (
          <pre
            className="p-6 w-full h-full overflow-auto font-mono text-sm leading-relaxed"
            style={{
              whiteSpace: 'pre-wrap',
              background: 'var(--color-bg)',
              color: 'var(--color-text)',
            }}
          >
            {canvasContent}
          </pre>
        );
      default:
        return null;
    }
  };

  const getIcon = () => {
    if (canvasLoading) return <Loader2 size={16} style={{ animation: 'spin 1.2s linear infinite' }} />;
    switch (canvasType) {
      case 'url': return <Globe size={16} />;
      case 'code': return <FileText size={16} />;
      case 'pdf': return <FileText size={16} />;
      default: return null;
    }
  };

  const getTitle = () => {
    if (canvasTitle) return canvasTitle;
    if (canvasLoading) return 'Building...';
    switch (canvasType) {
      case 'url': return 'Web Preview';
      case 'code': return 'Code';
      case 'pdf': return 'Document';
      default: return 'Canvas';
    }
  };


  return (
    <div
      className="flex h-full shrink-0 relative"
      style={{
        width: `${width}px`,
        background: 'var(--color-bg)',
      }}
    >
      {/* Resizer Handle */}
      <div
        className="absolute left-0 top-0 bottom-0 w-2 hover:bg-black/10 z-50 cursor-col-resize flex flex-col justify-center items-center group"
        onMouseDown={(e) => {
          e.preventDefault();
          setIsResizing(true);
        }}
        style={{
          transform: 'translateX(-50%)',
        }}
      >
        <div className="h-8 w-1 rounded-full bg-black/20 group-hover:bg-black/40 transition-colors" />
      </div>

      <div className="flex-1 flex flex-col h-full overflow-hidden" style={{ borderLeft: '1px solid var(--color-border)' }}>
        {/* Header */}
        <div
          className="flex items-center justify-between px-4 py-3 shrink-0"
          style={{ borderBottom: '1px solid var(--color-border)' }}
        >
          <div className="flex items-center gap-2 text-sm font-medium" style={{ color: 'var(--color-text)' }}>
            {getIcon()}
            <span className="truncate max-w-[200px]">{getTitle()}</span>
          </div>
          <div className="flex items-center gap-1">
            {canvasType === 'pdf' && !canvasLoading && canvasContent && (
              <a
                href={canvasContent}
                download
                className="p-1.5 rounded-md transition-colors"
                style={{ color: 'var(--color-text-secondary)' }}
                title="Download PDF"
              >
                <Download size={15} />
              </a>
            )}
            {(canvasType === 'url' || canvasType === 'pdf') && !canvasLoading && canvasContent && (
              <a
                href={canvasContent}
                target="_blank"
                rel="noreferrer"
                className="p-1.5 rounded-md transition-colors"
                style={{ color: 'var(--color-text-secondary)' }}
                title="Open in new tab"
              >
                <ExternalLink size={15} />
              </a>
            )}
            <button
              onClick={() => setCanvasOpen(false)}
              className="p-1.5 rounded-md transition-colors cursor-pointer"
              style={{ color: 'var(--color-text-secondary)' }}
              title="Close"
            >
              <X size={15} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-h-0 relative">
          {renderContent()}
          {/* Overlay to prevent iframe from capturing mouse events while resizing */}
          {isResizing && <div className="absolute inset-0 z-50" />}
        </div>

        {/* Inline CSS for animations */}
        <style>{`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          @keyframes shimmer {
            from { opacity: 0.3; }
            to { opacity: 0.7; }
          }
        `}</style>
      </div>
    </div>
  );
}
