import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useQuery } from '@tanstack/react-query';
import { getMetrics } from '@/lib/api';
import { CountyMetric } from '@/types';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

// Fix for default marker icon
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface CountyMapProps {
  filteredCounty?: string;
  counties?: CountyMetric[];
}

export function CountyMap({ filteredCounty, counties: propCounties }: CountyMapProps = {}) {
  // If counties are provided, use them directly (no loading needed)
  // Otherwise, fetch metrics (but it's instant with dummy data)
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['metrics', filteredCounty, '30d'], // Use default timeRange
    queryFn: () => getMetrics(filteredCounty, '30d'),
    enabled: !propCounties, // Only fetch if counties not provided
    staleTime: 0,
    gcTime: 0,
  });

  if (isLoading && !propCounties) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>County Query Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="w-full h-[400px]" />
        </CardContent>
      </Card>
    );
  }

  const counties = propCounties || metrics?.countySummary || [];
  
  // If a specific county is filtered, center the map on that county
  const centerCounty = filteredCounty && counties.length > 0
    ? counties.find(c => c.countyName === filteredCounty)
    : null;
  
  const mapCenter = centerCounty 
    ? centerCounty.coordinates 
    : [-1.286389, 36.817223]; // Default to Kenya center
  const mapZoom = centerCounty ? 9 : 7;

  return (
    <Card className="border-2 shadow-lg">
      <CardHeader>
        <CardTitle className="font-display text-2xl">
          County Query Distribution
          {filteredCounty && filteredCounty !== 'all' && ` - ${filteredCounty}`}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="w-full h-[400px] rounded-lg overflow-hidden border-2 border-border shadow-md">
          {counties.length > 0 ? (
            <MapContainer
              center={mapCenter as [number, number]}
              zoom={mapZoom}
              className="w-full h-full"
              scrollWheelZoom={false}
              key={`${mapCenter[0]}-${mapCenter[1]}-${mapZoom}`}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {counties.map((county) => (
                <Marker key={county.countyName} position={county.coordinates}>
                  <Popup>
                    <div className="p-2 min-w-[200px]">
                      <h3 className="font-bold text-base mb-2">{county.countyName}</h3>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Queries:</span>
                          <span className="font-medium">{county.queries.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Satisfaction:</span>
                          <span className="font-medium">{county.satisfaction}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Escalations:</span>
                          <span className="font-medium">{county.escalations}</span>
                        </div>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-muted/20">
              <p className="text-muted-foreground">No county data available</p>
            </div>
          )}
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Click on markers to view county details. Shows real-time query distribution powered by AfroKen LLM analytics.
        </p>
      </CardContent>
    </Card>
  );
}
