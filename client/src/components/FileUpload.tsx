import { useState, useRef, DragEvent } from 'react';

interface FileUploadProps {
    files: File[];
    onFilesChange: (files: File[]) => void;
}

const FileUpload = ({ files, onFilesChange }: FileUploadProps) => {
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);

        const droppedFiles = Array.from(e.dataTransfer.files).filter(file =>
            ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'].includes(file.type)
        );

        onFilesChange([...files, ...droppedFiles]);
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const selectedFiles = Array.from(e.target.files);
            onFilesChange([...files, ...selectedFiles]);
        }
    };

    const removeFile = (index: number) => {
        onFilesChange(files.filter((_, i) => i !== index));
    };

    return (
        <div>
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                style={{
                    border: `2px dashed ${isDragging ? 'var(--color-red-primary)' : 'var(--color-gray-light)'}`,
                    borderRadius: 'var(--radius-lg)',
                    padding: 'var(--spacing-2xl)',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all var(--transition-normal)',
                    background: isDragging ? 'var(--color-cream-dark)' : 'var(--color-white)',
                    position: 'relative',
                    overflow: 'hidden',
                }}
            >
                <div
                    style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '100%',
                        background: isDragging
                            ? 'linear-gradient(135deg, rgba(220, 38, 38, 0.05), rgba(220, 38, 38, 0.1))'
                            : 'transparent',
                        transition: 'background var(--transition-normal)',
                    }}
                />
                <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".jpg,.jpeg,.png,.pdf"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                />
                <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{
                        width: '64px',
                        height: '64px',
                        margin: '0 auto var(--spacing-md)',
                        background: 'linear-gradient(135deg, var(--color-red-primary), var(--color-red-dark))',
                        borderRadius: 'var(--radius-full)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 'var(--font-size-3xl)',
                        color: 'white',
                        boxShadow: 'var(--shadow-glossy)',
                    }}>
                        📁
                    </div>
                    <h4 style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--color-black)' }}>
                        {isDragging ? 'Drop files here' : 'Upload Documents'}
                    </h4>
                    <p style={{ color: 'var(--color-gray)', fontSize: 'var(--font-size-sm)', margin: 0 }}>
                        Drag and drop or click to browse
                    </p>
                    <p style={{ color: 'var(--color-gray)', fontSize: 'var(--font-size-xs)', marginTop: 'var(--spacing-xs)' }}>
                        Supported: JPG, PNG, PDF
                    </p>
                </div>
            </div>

            {files.length > 0 && (
                <div style={{ marginTop: 'var(--spacing-lg)' }}>
                    <h5 style={{ marginBottom: 'var(--spacing-md)', color: 'var(--color-black)' }}>
                        Selected Files ({files.length})
                    </h5>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                        {files.map((file, index) => (
                            <div
                                key={index}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    padding: 'var(--spacing-md)',
                                    background: 'var(--color-white)',
                                    border: '1px solid var(--color-gray-light)',
                                    borderRadius: 'var(--radius-md)',
                                    transition: 'all var(--transition-fast)',
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.borderColor = 'var(--color-red-primary)';
                                    e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.borderColor = 'var(--color-gray-light)';
                                    e.currentTarget.style.boxShadow = 'none';
                                }}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                                    <div style={{
                                        width: '40px',
                                        height: '40px',
                                        background: 'var(--color-cream-dark)',
                                        borderRadius: 'var(--radius-md)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: 'var(--font-size-lg)',
                                    }}>
                                        {file.type.includes('pdf') ? '📄' : '🖼️'}
                                    </div>
                                    <div>
                                        <p style={{ margin: 0, fontWeight: 500, color: 'var(--color-black)', fontSize: 'var(--font-size-sm)' }}>
                                            {file.name}
                                        </p>
                                        <p style={{ margin: 0, color: 'var(--color-gray)', fontSize: 'var(--font-size-xs)' }}>
                                            {(file.size / 1024).toFixed(2)} KB
                                        </p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => removeFile(index)}
                                    style={{
                                        background: 'var(--color-red-lighter)',
                                        color: 'var(--color-red-dark)',
                                        border: 'none',
                                        width: '32px',
                                        height: '32px',
                                        borderRadius: 'var(--radius-full)',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: 'var(--font-size-sm)',
                                        fontWeight: 'bold',
                                        transition: 'all var(--transition-fast)',
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = 'var(--color-red-primary)';
                                        e.currentTarget.style.color = 'white';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = 'var(--color-red-lighter)';
                                        e.currentTarget.style.color = 'var(--color-red-dark)';
                                    }}
                                >
                                    ✕
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default FileUpload;
