'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'

interface FileUploadProps {
  onFileSelect: (file: File) => void
  uploading: boolean
  analyzing: boolean
}

export default function FileUpload({ onFileSelect, uploading, analyzing }: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      
      // 检查是否是 DWG 文件
      const isDwg = file.name.toLowerCase().endsWith('.dwg')
      
      if (isDwg) {
        // 显示警告但仍然允许上传
        const userConfirm = window.confirm(
          'DWG 格式支持有限\n\n' +
          '当前系统对 DWG 格式的支持还不完善，可能导致分析失败。\n\n' +
          '建议：\n' +
          '1. 在 CAD 软件中将文件另存为 DXF 格式\n' +
          '2. 然后上传 DXF 文件进行分析\n\n' +
          '是否继续上传 DWG 文件？'
        )
        
        if (!userConfirm) {
          return
        }
      }
      
      setSelectedFile(file)
      onFileSelect(file)
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/dxf': ['.dxf'],
      'application/acad': ['.dwg'],
      'application/x-acad': ['.dwg'],
      'application/autocad_drawing': ['.dwg'],
      'image/vnd.dwg': ['.dwg'],
      'image/x-dwg': ['.dwg'],
      'application/x-dwg': ['.dwg'],
      'application/octet-stream': ['.dxf', '.dwg']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    disabled: uploading || analyzing,
    noClick: false,
    noKeyboard: false,
    multiple: false
  })

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer
        transition-all duration-300
        ${isDragActive 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-300 bg-white hover:border-blue-400 hover:bg-blue-50'
        }
        ${(uploading || analyzing) && 'opacity-50 cursor-not-allowed'}
      `}
    >
      <input {...getInputProps()} id="file-upload-input" />

      {/* 图标 */}
      <div className="mb-4">
        <svg
          className="mx-auto h-16 w-16 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
      </div>

      {/* 文字提示 */}
      <div>
        {isDragActive ? (
          <p className="text-lg font-medium text-blue-600">
            松开鼠标上传文件
          </p>
        ) : selectedFile ? (
          <div>
            <p className="text-lg font-medium text-green-600 mb-2">
              ✓ 已选择文件
            </p>
            <p className="text-gray-600">
              {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
            </p>
          </div>
        ) : (
          <div>
            <p className="text-lg font-medium text-gray-700 mb-2">
              拖放 CAD 文件到此处，或点击选择文件
            </p>
            <p className="text-sm text-gray-500">
              推荐使用 .dxf 格式，最大 10MB
            </p>
            <p className="text-xs text-amber-600 mt-2">
              ⚠️ DWG 格式支持有限，建议转换为 DXF
            </p>
          </div>
        )}
      </div>

      {/* 文件格式提示 */}
      {!selectedFile && !uploading && !analyzing && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            支持的标准：GB/T 14665-2012 机械工程CAD制图规则
          </p>
        </div>
      )}
    </div>
  )
}
