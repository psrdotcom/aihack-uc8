import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { DigestDetailCard } from "@/components/dashboard/DigestDetailCard";
import { DigestHistoryCard } from "@/components/dashboard/DigestHistoryCard";
const historyDataTop = [
  { date: "June 27", detail: "85 Articles PDF" },
  { date: "June 25", detail: "5 Topics Created" },
  { date: "June 24", detail: "42 arrinedo PDF" },
  { date: "June 23", detail: "Download PDF" },
];

const historyDataBottom = [
  { date: "June 27", detail: "33 Articles PDF" },
  { date: "June 25", detail: "30 articles PDF" },
  { date: "June 23", detail: "Download PDF" },
];


export default function Page() {
  return (
    // <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
    //   <div className="grid auto-rows-min gap-4 md:grid-cols-3">
    //     <div className="bg-muted/50 aspect-video rounded-xl" />
    //     <div className="bg-muted/50 aspect-video rounded-xl" />
    //     <div className="bg-muted/50 aspect-video rounded-xl" />
    //   </div>
    //   <div className="bg-muted/50 min-h-[100vh] flex-1 rounded-xl md:min-h-min" />
    // </div>
    <div className="min-h-screen bg-background p-4 sm:p-6 lg:p-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full max-w-7xl mx-auto">
        <DashboardCard />
        <DigestHistoryCard title="Digest History" data={historyDataTop} />
        <DigestDetailCard />
        <DigestHistoryCard title="Digest History" data={historyDataBottom} />
      </div>
    </div>
  )
}
