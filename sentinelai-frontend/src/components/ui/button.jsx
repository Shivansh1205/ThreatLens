import * as React from "react"
import { cn } from "../../lib/utils"

const Button = React.forwardRef(({ className, variant = "default", size = "default", ...props }, ref) => {
  const variants = {
    default: "bg-primary text-white hover:bg-primary/90 shadow-[0_0_10px_rgba(59,130,246,0.2)]",
    danger: "bg-danger text-white hover:bg-danger/90 shadow-[0_0_10px_rgba(239,68,68,0.2)]",
    outline: "border border-white/10 bg-transparent hover:bg-white/5 text-zinc-200",
    ghost: "hover:bg-white/5 text-zinc-300 hover:text-white",
  }
  
  const sizes = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3",
    lg: "h-11 rounded-md px-8",
    icon: "h-10 w-10",
  }
  
  return (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    />
  )
})
Button.displayName = "Button"

export { Button }
