import { useState } from 'react'

interface Props {
  src: string
  alt: string
}

export default function ImageViewer({ src, alt }: Props) {
  const [zoomed, setZoomed] = useState(false)

  return (
    <div
      onClick={() => setZoomed((z) => !z)}
      style={{ cursor: zoomed ? 'zoom-out' : 'zoom-in', overflow: 'auto' }}
    >
      <img
        src={src}
        alt={alt}
        style={{
          maxWidth: zoomed ? 'none' : '100%',
          transform: zoomed ? 'scale(1.5)' : 'scale(1)',
          transformOrigin: 'top left',
          transition: 'transform 0.2s',
        }}
        onError={(e) => {
          (e.target as HTMLImageElement).style.display = 'none'
        }}
      />
    </div>
  )
}
