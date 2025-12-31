import type { Widget } from '../../lib/api-types';
import KPIWidget from './KPIWidget';
import ChartWidget from './ChartWidget';

interface WidgetRendererProps {
  widget: Widget;
  title?: string;
}

export default function WidgetRenderer({ widget, title }: WidgetRendererProps) {
  switch (widget.type) {
    case 'kpi':
      return <KPIWidget widget={widget} />;
    
    case 'chart':
      return <ChartWidget widget={widget} title={title} />;
    
    default:
      return (
        <div className="bg-white border border-neutral-200 rounded-lg p-6">
          <p className="text-neutral-500">Unsupported widget type: {widget.type}</p>
        </div>
      );
  }
}
