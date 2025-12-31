
import { LineChart, Line, BarChart, Bar, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { Widget } from '../../lib/api-types';

interface ChartWidgetProps {
  widget: Widget;
  title?: string;
}

export default function ChartWidget({ widget, title }: ChartWidgetProps) {
  if (!widget.data || widget.data.length === 0) {
    return (
      <div className="bg-white border border-neutral-200 rounded-lg p-6">
        <h3 className="text-neutral-900 mb-4">{title || 'Chart'}</h3>
        <div className="h-[300px] flex items-center justify-center text-neutral-500">
          No data available
        </div>
      </div>
    );
  }

  const xKey = widget.x || 'x';
  const yKey = widget.y || 'y';

  const renderChart = () => {
    switch (widget.chart_type) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={widget.data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis dataKey={xKey} stroke="#737373" />
              <YAxis stroke="#737373" />
              <Tooltip />
              <Line type="monotone" dataKey={yKey} stroke="#171717" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={widget.data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis dataKey={xKey} stroke="#737373" />
              <YAxis stroke="#737373" />
              <Tooltip />
              <Bar dataKey={yKey} fill="#171717" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis dataKey={xKey} stroke="#737373" />
              <YAxis dataKey={yKey} stroke="#737373" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={widget.data} fill="#171717" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      default:
        return (
          <div className="h-[300px] flex items-center justify-center text-neutral-500">
            Unsupported chart type: {widget.chart_type}
          </div>
        );
    }
  };

  return (
    <div className="bg-white border border-neutral-200 rounded-lg p-6">
      <h3 className="text-neutral-900 mb-4">
        {title || `${yKey} by ${xKey}`}
        {widget.aggregation && <span className="text-neutral-600"> ({widget.aggregation})</span>}
      </h3>
      {renderChart()}
    </div>
  );
}
