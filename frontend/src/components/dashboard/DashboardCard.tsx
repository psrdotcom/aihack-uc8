import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MoreVertical } from "lucide-react";

export function DashboardCard() {
  return (
    <Card className="col-span-1 shadow-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 bg-[hsl(var(--custom-header-bg))] text-[hsl(var(--custom-header-fg))] rounded-t-lg">
        <CardTitle className="text-xl font-bold">Dashboard</CardTitle>
        <MoreVertical className="h-5 w-5 cursor-pointer" />
      </CardHeader>
      <CardContent className="pt-6">
        <div className="bg-[hsl(var(--custom-dashboard-inner-bg))] p-6 rounded-lg">
          <div className="text-center">
            <h3 className="text-2xl font-semibold text-foreground">
              June 27 Digest
            </h3>
            <Button className="mt-4 px-8 py-2">Download PDF</Button>
          </div>
        </div>
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
          <StatBox value="85" label="Articles Processed" />
          <StatBox value="5" label="Topics Created" />
          <StatBox value="42" label="Time Taken" />
        </div>
      </CardContent>
    </Card>
  );
}

function StatBox({ value, label }: { value: string; label: string }) {
  return (
    <div className="bg-card p-4 rounded-lg border">
      <p className="text-3xl font-bold text-foreground">{value}</p>
      <p className="text-sm text-muted-foreground">{label}</p>
    </div>
  );
}