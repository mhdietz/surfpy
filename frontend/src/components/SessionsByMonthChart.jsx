import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import Card from './UI/Card';

function SessionsByMonthChart({ data }) {
  if (!data || data.length === 0) {
    return null;
  }

  return (
    <Card className="mt-8">
      <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">Sessions by Month</h3>
      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <BarChart
            data={data}
            margin={{
              top: 5,
              right: 20,
              left: -10,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="month" tick={{ fontSize: 12 }} />
            <YAxis allowDecimals={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                border: '1px solid #ccc',
                borderRadius: '5px',
              }}
              labelStyle={{ fontWeight: 'bold' }}
            />
            <Bar dataKey="count" fill="#3B82F6" name="Sessions" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

export default SessionsByMonthChart;
