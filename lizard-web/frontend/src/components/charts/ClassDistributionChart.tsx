import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { ClassDistribution } from '../../types/op'

interface Props {
  data: ClassDistribution[]
}

export default function ClassDistributionChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="class" />
        <YAxis />
        <Tooltip formatter={(value) => [`${value}`, 'Couros']} />
        <Bar dataKey="count" fill="#4f46e5" />
      </BarChart>
    </ResponsiveContainer>
  )
}
