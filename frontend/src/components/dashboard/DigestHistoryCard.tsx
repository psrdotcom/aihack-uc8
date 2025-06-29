import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table";
import { MoreVertical } from "lucide-react";
import { DatePicker } from "../date-picker";
import { useState } from "react";

type HistoryItem = {
  date: string;
  detail: string;
};

interface DigestHistoryCardProps {
  title: string;
  data: HistoryItem[];
}

export function DigestHistoryCard({ title, data }: DigestHistoryCardProps) {
  const [getDate, setDate] = useState(new Date());
  const handleDateChange = (value: any) => {
    if(value != null && value != undefined)
      setDate(value);
  }
  // const filtered = data.filter((item:HistoryItem, index: number) => { item.date === DatePicker.}
  return (
    <Card className="col-span-1 shadow-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 bg-[hsl(var(--custom-header-bg))] text-[hsl(var(--custom-header-fg))] rounded-t-lg">
        <CardTitle className="text-xl font-bold">{title}</CardTitle>
        <MoreVertical className="h-5 w-5 cursor-pointer" />
      </CardHeader>
      <CardContent className="pt-6">
        <div className="relative mb-4">
          {/* <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" /> */}
          <DatePicker value={getDate} onChange={handleDateChange}/>
          {/* <Input placeholder="Date" className="pl-10" /> */}
        </div>
        <Table>
          <TableBody>
            {data.map((item, index) => (
              <TableRow key={index}>
                <TableCell className="font-medium">{item.date}</TableCell>
                <TableCell className="text-right">{item.detail}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}