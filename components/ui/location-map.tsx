"use client"

import type React from "react"
import { useState, useRef } from "react"
import { motion, AnimatePresence, useMotionValue, useTransform, useSpring } from "framer-motion"

const MAPS_URL = "https://maps.app.goo.gl/rBH1wQP3uLcpV1GJ6"

const BRAND = {
  orange: "#ff5500",
  black: "#0a0a0a",
  cream: "#f0ebe0",
} as const

interface LocationMapProps {
  location?: string
  coordinates?: string
  className?: string
}

export function LocationMap({
  location = "Praia Barra Norte, BC",
  coordinates = "26°58'03\"S, 48°38'03\"O",
  className,
}: LocationMapProps) {
  const [isHovered, setIsHovered] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  const rotateX = useTransform(mouseY, [-50, 50], [8, -8])
  const rotateY = useTransform(mouseX, [-50, 50], [-8, 8])

  const springRotateX = useSpring(rotateX, { stiffness: 300, damping: 30 })
  const springRotateY = useSpring(rotateY, { stiffness: 300, damping: 30 })

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    mouseX.set(e.clientX - centerX)
    mouseY.set(e.clientY - centerY)
  }

  const handleMouseLeave = () => {
    mouseX.set(0)
    mouseY.set(0)
    setIsHovered(false)
  }

  const handleClick = () => {
    setIsExpanded(!isExpanded)
  }

  const handleOpenMaps = (e: React.MouseEvent) => {
    e.stopPropagation()
    window.open(MAPS_URL, "_blank", "noopener,noreferrer")
  }

  return (
    <motion.div
      ref={containerRef}
      className={`relative select-none ${className ?? ""}`}
      style={{ perspective: 1000, cursor: "pointer" }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
    >
      <motion.div
        className="relative overflow-hidden rounded-none border-2"
        style={{
          rotateX: springRotateX,
          rotateY: springRotateY,
          transformStyle: "preserve-3d",
          borderColor: BRAND.black,
          backgroundColor: BRAND.cream,
        }}
        animate={{
          width: isExpanded ? 500 : 360,
          height: isExpanded ? 340 : 160,
        }}
        transition={{ type: "spring", stiffness: 400, damping: 35 }}
      >
        {/* Expanded map content */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              className="absolute inset-0 pointer-events-none"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4, delay: 0.1 }}
            >
              {/* Map background */}
              <div className="absolute inset-0" style={{ backgroundColor: "#e8e0d0" }} />

              <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
                {/* Ocean/water area */}
                <rect x="0" y="60%" width="100%" height="40%" fill="#c8d8e8" opacity="0.5" />

                {/* Main roads */}
                <motion.line x1="0%" y1="38%" x2="100%" y2="38%"
                  stroke={BRAND.black} strokeOpacity="0.3" strokeWidth="4"
                  initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                  transition={{ duration: 0.8, delay: 0.2 }} />
                <motion.line x1="0%" y1="62%" x2="100%" y2="62%"
                  stroke={BRAND.black} strokeOpacity="0.2" strokeWidth="3"
                  initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                  transition={{ duration: 0.8, delay: 0.3 }} />

                {/* Vertical roads */}
                <motion.line x1="35%" y1="0%" x2="35%" y2="100%"
                  stroke={BRAND.black} strokeOpacity="0.2" strokeWidth="3"
                  initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                  transition={{ duration: 0.6, delay: 0.4 }} />
                <motion.line x1="65%" y1="0%" x2="65%" y2="100%"
                  stroke={BRAND.black} strokeOpacity="0.2" strokeWidth="3"
                  initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                  transition={{ duration: 0.6, delay: 0.5 }} />

                {/* Secondary streets */}
                {[20, 50, 80].map((y, i) => (
                  <motion.line key={`h-${i}`} x1="0%" y1={`${y}%`} x2="100%" y2={`${y}%`}
                    stroke={BRAND.black} strokeOpacity="0.08" strokeWidth="1.5"
                    initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                    transition={{ duration: 0.5, delay: 0.6 + i * 0.1 }} />
                ))}
                {[15, 50, 85].map((x, i) => (
                  <motion.line key={`v-${i}`} x1={`${x}%`} y1="0%" x2={`${x}%`} y2="100%"
                    stroke={BRAND.black} strokeOpacity="0.08" strokeWidth="1.5"
                    initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                    transition={{ duration: 0.5, delay: 0.7 + i * 0.1 }} />
                ))}

                {/* Beach line */}
                <motion.line x1="0%" y1="72%" x2="100%" y2="70%"
                  stroke={BRAND.orange} strokeOpacity="0.4" strokeWidth="2" strokeDasharray="6 4"
                  initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                  transition={{ duration: 1, delay: 0.5 }} />
              </svg>

              {/* Buildings */}
              {[
                { top: "42%", left: "8%", w: "14%", h: "18%" },
                { top: "18%", left: "38%", w: "11%", h: "14%" },
                { top: "20%", right: "8%", w: "12%", h: "22%" },
                { top: "55%", left: "5%", w: "8%", h: "10%" },
                { top: "10%", left: "72%", w: "13%", h: "10%" },
              ].map((pos, i) => (
                <motion.div
                  key={i}
                  className="absolute rounded-sm border"
                  style={{
                    ...pos,
                    backgroundColor: `${BRAND.black}22`,
                    borderColor: `${BRAND.black}18`,
                  }}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: 0.5 + i * 0.1 }}
                />
              ))}

              {/* Pin */}
              <motion.div
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-full"
                initial={{ scale: 0, y: -20 }}
                animate={{ scale: 1, y: 0 }}
                transition={{ type: "spring", stiffness: 400, damping: 20, delay: 0.3 }}
              >
                <svg width="28" height="36" viewBox="0 0 24 32" fill="none"
                  style={{ filter: `drop-shadow(0 2px 8px ${BRAND.orange}88)` }}>
                  <path
                    d="M12 0C7.03 0 3 4.03 3 9c0 6.75 9 23 9 23s9-16.25 9-23c0-4.97-4.03-9-9-9z"
                    fill={BRAND.orange}
                  />
                  <circle cx="12" cy="9" r="3.5" fill={BRAND.cream} />
                </svg>
              </motion.div>

              {/* Gradient fade bottom */}
              <div
                className="absolute inset-0 pointer-events-none"
                style={{ background: `linear-gradient(to top, ${BRAND.cream}cc, transparent 50%)` }}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Grid pattern — only collapsed */}
        <motion.div
          className="absolute inset-0"
          animate={{ opacity: isExpanded ? 0 : 1 }}
          transition={{ duration: 0.3 }}
        >
          <svg width="100%" height="100%" className="absolute inset-0" opacity="0.04">
            <defs>
              <pattern id="aviva-grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke={BRAND.black} strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#aviva-grid)" />
          </svg>
        </motion.div>

        {/* Content layer */}
        <div className="relative z-10 h-full flex flex-col justify-between p-4">
          {/* Top row */}
          <div className="flex items-start justify-between">
            <motion.div animate={{ opacity: isExpanded ? 0 : 1 }} transition={{ duration: 0.25 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke={BRAND.orange} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
                <line x1="9" x2="9" y1="3" y2="18" />
                <line x1="15" x2="15" y1="6" y2="21" />
              </svg>
            </motion.div>

            {/* Praia Barra Norte badge */}
            <motion.div
              className="flex items-center gap-1.5 px-2 py-1"
              style={{
                border: `1px solid ${BRAND.black}22`,
                backgroundColor: `${BRAND.black}08`,
              }}
              animate={{ scale: isHovered ? 1.05 : 1 }}
              transition={{ duration: 0.2 }}
            >
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: BRAND.orange }} />
              <span
                className="font-mono text-[9px] uppercase tracking-widest"
                style={{ color: BRAND.black, opacity: 0.6 }}
              >
                BC
              </span>
            </motion.div>
          </div>

          {/* Bottom */}
          <div className="space-y-1.5">
            <motion.h3
              className="font-fjalla text-sm uppercase tracking-wider"
              style={{ color: BRAND.black }}
              animate={{ x: isHovered ? 4 : 0 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
            >
              {location}
            </motion.h3>

            <AnimatePresence>
              {isExpanded && (
                <motion.p
                  className="font-mono text-[10px]"
                  style={{ color: `${BRAND.black}80` }}
                  initial={{ opacity: 0, y: -8, height: 0 }}
                  animate={{ opacity: 1, y: 0, height: "auto" }}
                  exit={{ opacity: 0, y: -8, height: 0 }}
                  transition={{ duration: 0.25 }}
                >
                  {coordinates}
                </motion.p>
              )}
            </AnimatePresence>

            {/* Underline */}
            <motion.div
              className="h-px"
              style={{ background: `linear-gradient(to right, ${BRAND.orange}80, ${BRAND.orange}20, transparent)` }}
              initial={{ scaleX: 0, originX: 0 }}
              animate={{ scaleX: isHovered || isExpanded ? 1 : 0.3 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
            />

            {/* Open Maps button — only expanded */}
            <AnimatePresence>
              {isExpanded && (
                <motion.button
                  onClick={handleOpenMaps}
                  className="mt-1 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest"
                  style={{ color: BRAND.orange, pointerEvents: "all" }}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 4 }}
                  transition={{ duration: 0.2, delay: 0.15 }}
                  whileHover={{ x: 2 }}
                >
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <polyline points="15 3 21 3 21 9" />
                    <line x1="10" y1="14" x2="21" y2="3" />
                  </svg>
                  Abrir no Maps →
                </motion.button>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>

      {/* Hint */}
      <motion.p
        className="absolute -bottom-6 left-1/2 font-mono text-[9px] uppercase tracking-widest whitespace-nowrap"
        style={{ x: "-50%", color: `${BRAND.black}60` }}
        initial={{ opacity: 0 }}
        animate={{ opacity: isHovered && !isExpanded ? 1 : 0, y: isHovered ? 0 : 4 }}
        transition={{ duration: 0.2 }}
      >
        Clique para expandir
      </motion.p>
    </motion.div>
  )
}
