import { Card } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useRef } from 'react';
import { useReactToPrint } from 'react-to-print';
// import { useReactToPrint } from 'react-to-print';
 
function About() {
 let componentRef = useRef(null);

  const handlePrint = useReactToPrint({
    contentRef: componentRef,
    documentTitle: `${'test'}-Print`,
    onPrintError: () => alert("there is an error when printing"),
  });
  return (
    <div className="grid p-8" ref={componentRef}>
      <h2 className="text-2xl font-bold mb-4">About</h2>
      <p>About this application.</p>
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">
        <Card className="xl:col-span-1 col-span-1">
          <h2>
            <img src="/vite.svg" alt="Logo" className="w-32 h-32 object-contain rounded p-5" />
          </h2>
        </Card>
        <Card className="xl:col-span-3 col-span-1">
          <div className="px-8">
            <h2>Name 1</h2>
            <span>Some description sits here</span>
            <Separator />
            <h2 className="pt-4">Name 1</h2>
            <span>Some description sits here</span>
            <Separator />
            <h2 className="pt-4">Name 1</h2>
            <span>Some description sits here</span>
            <Separator />
          </div>
        </Card>
      </div>
      <div className="print:hidden">
          <button
            onClick={handlePrint}
            className="bg-cyan-500 px-6 py-2 text-white border border-cyan-500 font-bold rounded-md mb-3 w-full lg:w-fit my-6 max-w-sm"
          >
            Print Payslip
          </button>
        </div>
    </div>
  );
}

export default About;
