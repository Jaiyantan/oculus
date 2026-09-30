import React from 'react';
import './cards.css';
import LedText from './LedText';

export default function GlassCard({ 
  variant = 'speed', // 'speed', 'context', 'connections'
  title, 
  metric, 
  unit = '', 
  caption, 
  children 
}) {
  return (
    <div className={`glass-card-container card--${variant}`}>
      <svg className="card__grain" viewBox="0 0 429 554">
        <filter id={`cardNoise-${variant}`}>
          <feTurbulence type="fractalNoise" baseFrequency=".54" numOctaves="3" seed="27" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
          <feComponentTransfer>
            <feFuncR type="linear" slope="1.8" intercept="-.25" />
            <feFuncG type="linear" slope="1.8" intercept="-.25" />
            <feFuncB type="linear" slope="1.8" intercept="-.25" />
            <feFuncA type="table" tableValues="0 .52" />
          </feComponentTransfer>
        </filter>
        <rect width="100%" height="100%" filter={`url(#cardNoise-${variant})`} />
      </svg>
      
      <div className="glass-card-content">
        {title && <h3 className="glass-card-title">{title}</h3>}
        
        {children}
        
        <div className="glass-card-metric">
          {metric && <LedText text={metric} size="large" />}
          {unit && <span className="glass-card-unit">{unit}</span>}
        </div>
        
        {caption && <div className="glass-card-caption">{caption}</div>}
      </div>
    </div>
  );
}
