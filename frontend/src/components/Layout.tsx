import { SidebarInset, SidebarProvider, SidebarTrigger } from "./ui/sidebar";
import { AppSidebar } from "./app-sidebar";
import { Separator } from "@radix-ui/react-separator";
import { ThemeProvider } from "next-themes";
import { ModeToggle } from "./modeToggle";
import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbPage } from "./ui/breadcrumb";

export default function Layout({ children }: { children: React.ReactNode }) {
    return (
        // <SidebarProvider>
        //     <AppSidebar />
        //     <main className="flex-1 flex flex-col items-center justify-center min-h-screen p-8 pl-0 md:pl-56 transition-all duration-300">
        //       {children}
        //     </main>
        //     <SidebarTrigger className="fixed top-4 left-4 z-50" />
        // </SidebarProvider>
        <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
        >
            <SidebarProvider>
                <AppSidebar />
                <SidebarInset>
                    <header className="flex h-16 shrink-0 items-center gap-2">
                        <div className="grow flex items-center gap-2 px-4">
                            <SidebarTrigger className="-ml-1" />
                            <Separator
                                orientation="vertical"
                                className="mr-2 data-[orientation=vertical]:h-4"
                            />
                            <Breadcrumb>
                                <BreadcrumbList>
                                    <BreadcrumbItem className="hidden md:block">
                                        <BreadcrumbLink href="#">
                                            Building Your Application
                                        </BreadcrumbLink>
                                    </BreadcrumbItem>
                                    <BreadcrumbSeparator className="hidden md:block" />
                                    <BreadcrumbItem>
                                        <BreadcrumbPage>Data Fetching</BreadcrumbPage>
                                    </BreadcrumbItem>
                                </BreadcrumbList>
                            </Breadcrumb>

                        </div>
                        <ModeToggle />
                    </header>
                    {/* <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <div className="grid auto-rows-min gap-4 md:grid-cols-3">
            <div className="bg-muted/50 aspect-video rounded-xl" />
            <div className="bg-muted/50 aspect-video rounded-xl" />
            <div className="bg-muted/50 aspect-video rounded-xl" />
          </div>
          <div className="bg-muted/50 min-h-[100vh] flex-1 rounded-xl md:min-h-min" />
        </div> */}
                    {children}
                    {/* <main className="flex-1 flex flex-col items-center justify-center min-h-screen p-8 pl-0 md:pl-56 transition-all duration-300">
                        {children}
                    </main> */}
                </SidebarInset>
            </SidebarProvider>
        </ThemeProvider>
    );
}
