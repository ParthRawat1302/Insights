import type { Widget } from '../../lib/api-types';

interface KPIWidgetProps {
  widget: Widget;
}

export default function KPIWidget({ widget }: KPIWidgetProps) {
  console.log('KPIWidget widget:', widget);
  const formatValue = (value: number | undefined, format: string | null | undefined) => {
    if (value === undefined) return 'N/A';
    
    if (format === 'currency') {
      return `$${value.toLocaleString()}`;
    } else if (format === 'percentage') {
      return `${value.toFixed(2)}%`;
    } else if (format === 'number') {
      return value.toLocaleString();
    }
    
    return value.toLocaleString();
  };

  return (
    <div className="bg-white border border-neutral-200 rounded-lg p-6">
      <p className="text-neutral-600 mb-2">{widget.metric || 'Metric'}</p>
      <p className="text-neutral-900">{formatValue(widget.value, widget.format)}</p>
    </div>
  );
}
