"use client";

import { useEffect, useState } from "react";
import LiveMap, { type TruckPosition } from "@/components/map/live-map";
import StatCard from "@/components/ui/stat-card";

/** Simulated truck positions for demo (replaced by WebSocket in production). */
function generateDemoPositions(): TruckPosition[] {
  const statuses: TruckPosition["status"][] = [
    "available",
    "en_route",
    "loading",
    "offline",
  ];
  const trucks: TruckPosition[] = [
    { truck_id: "TRK-001", latitude: 30.0444, longitude: 31.2357, speed_kmh: 0, heading: 0, status: "available" },
    { truck_id: "TRK-002", latitude: 29.5952, longitude: 32.3414, speed_kmh: 85, heading: 270, status: "en_route" },
    { truck_id: "TRK-003", latitude: 31.2001, longitude: 29.8623, speed_kmh: 0, heading: 180, status: "loading" },
    { truck_id: "TRK-004", latitude: 29.9569, longitude: 30.9271, speed_kmh: 72, heading: 45, status: "en_route" },
    { truck_id: "TRK-005", latitude: 30.2975, longitude: 31.7629, speed_kmh: 0, heading: 0, status: "offline" },
    { truck_id: "TRK-006", latitude: 31.4175, longitude: 31.8125, speed_kmh: 90, heading: 200, status: "en_route" },
    { truck_id: "TRK-007", latitude: 30.0048, longitude: 32.5498, speed_kmh: 0, heading: 90, status: "available" },
    { truck_id: "TRK-008", latitude: 30.5965, longitude: 31.5017, speed_kmh: 60, heading: 315, status: "en_route" },
  ];

  // Slightly randomize positions on each tick
  return trucks.map((t) => ({
    ...t,
    latitude: t.latitude + (Math.random() - 0.5) * 0.01,
    longitude: t.longitude + (Math.random() - 0.5) * 0.01,
    speed_kmh: t.status === "en_route" ? t.speed_kmh + (Math.random() - 0.5) * 10 : 0,
    status: statuses[Math.floor(Math.random() * 100) % statuses.length] as TruckPosition["status"],
  }));
}

export default function DashboardPage() {
  const [positions, setPositions] = useState<TruckPosition[]>([]);

  useEffect(() => {
    // Initial positions
    setPositions(generateDemoPositions());

    // Simulate real-time updates every 3s
    const interval = setInterval(() => {
      setPositions(generateDemoPositions());
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const activeCount = positions.filter((p) => p.status !== "offline").length;
  const enRouteCount = positions.filter((p) => p.status === "en_route").length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">God View Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Real-time fleet monitoring across Egypt
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Active Trucks"
          value={activeCount}
          subtitle={`${positions.length} total registered`}
          trend="up"
          color="green"
        />
        <StatCard
          label="En Route"
          value={enRouteCount}
          subtitle="Currently on delivery"
          trend="neutral"
          color="blue"
        />
        <StatCard
          label="Today's Shipments"
          value={42}
          subtitle="+12% from yesterday"
          trend="up"
          color="blue"
        />
        <StatCard
          label="Revenue (EGP)"
          value="187,500"
          subtitle="Daily gross"
          trend="up"
          color="green"
        />
      </div>

      {/* Live Map */}
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card-bg)] p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Live Fleet Map</h2>
          <div className="flex items-center gap-4 text-xs">
            <span className="flex items-center gap-1.5">
              <span className="inline-block h-2.5 w-2.5 rounded-full bg-emerald-500" />
              Available
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block h-2.5 w-2.5 rounded-full bg-blue-500" />
              En Route
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block h-2.5 w-2.5 rounded-full bg-amber-500" />
              Loading
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block h-2.5 w-2.5 rounded-full bg-gray-500" />
              Offline
            </span>
          </div>
        </div>
        <LiveMap
          positions={positions}
          showHubs
          className="h-[500px] w-full"
        />
      </div>
    </div>
  );
}
