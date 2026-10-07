type Props = {
  label: string;
  value: string | number;
};

export function StatCard({ label, value }: Props) {
  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}

