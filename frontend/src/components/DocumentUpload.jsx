import React from 'react';
import { useDropzone } from 'react-dropzone';
import { FileUp, ShieldAlert, FileText } from 'lucide-react';

export function DocumentUpload({ onFileUpload, isUploading }) {
  const onDrop = (acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  };

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  return (
    <div className="w-full my-3 px-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-[#10504A] bg-[#E6F2F0]'
            : 'border-[#D6CBB8] bg-[#FAF8F3] hover:border-[#10504A] hover:bg-[#F4FAF9]'
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center space-y-2">
          <div className="p-3 bg-[#E6F2F0] text-[#10504A] rounded-full">
            <FileUp className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-ink">
              {isDragActive
                ? 'Drop your document here...'
                : 'Drop a document to ask about it directly'}
            </p>
            <p className="text-xs text-slate-custom mt-0.5">
              Supports rental agreements, notices, employment contracts (PDF or DOCX, max 10MB)
            </p>
          </div>
          {isUploading && (
            <div className="flex items-center gap-2 text-xs font-code-mono text-[#10504A] mt-2">
              <span className="w-3 h-3 border-2 border-[#10504A] border-t-transparent rounded-full animate-spin"></span>
              <span>Indexing document into session store...</span>
            </div>
          )}
        </div>
      </div>

      {fileRejections.length > 0 && (
        <div className="mt-2 flex items-center gap-2 text-xs text-rust bg-rust/10 p-2 rounded.md">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>File rejected: Please upload a PDF or DOCX under 10MB.</span>
        </div>
      )}
    </div>
  );
}
