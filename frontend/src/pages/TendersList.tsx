import React from 'react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Plus, Search, Filter } from 'lucide-react'

const TendersList: React.FC = () => {
  const mockTenders = [
    {
      id: 1,
      title: 'Qurilish materiallari yetkazib berish',
      status: 'active',
      budget: 500000000,
      deadline: '2024-02-15',
      participants: 12,
      category: 'Qurilish'
    },
    {
      id: 2,
      title: 'Ofis jihozlarini sotib olish',
      status: 'pending',
      budget: 120000000,
      deadline: '2024-02-20',
      participants: 8,
      category: 'Ofis'
    },
    {
      id: 3,
      title: 'IT infratuzukturasi modernizatsiyasi',
      status: 'active',
      budget: 850000000,
      deadline: '2024-03-01',
      participants: 15,
      category: 'IT'
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'completed':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'Faol'
      case 'pending':
        return 'Kutilmoqda'
      case 'completed':
        return 'Tugallangan'
      default:
        return status
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Tenderlar</h1>
          <p className="text-muted-foreground">Barcha tenderlarni boshqarish</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Yangi Tender
        </Button>
      </div>

      {/* Search and Filter */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Tenderlarni qidirish..."
            className="w-full pl-10 pr-4 py-2 border border-input bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <Button variant="outline">
          <Filter className="mr-2 h-4 w-4" />
          Filter
        </Button>
      </div>

      {/* Tenders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockTenders.map((tender) => (
          <Card key={tender.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{tender.title}</CardTitle>
                <Badge className={getStatusColor(tender.status)}>
                  {getStatusText(tender.status)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Byudjet:</span>
                  <span className="font-medium">
                    {new Intl.NumberFormat('uz-UZ', {
                      style: 'currency',
                      currency: 'UZS'
                    }).format(tender.budget)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Muddat:</span>
                  <span className="font-medium">{tender.deadline}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Ishtirokchilar:</span>
                  <span className="font-medium">{tender.participants}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Kategoriya:</span>
                  <Badge variant="outline">{tender.category}</Badge>
                </div>
              </div>
              <div className="mt-4 flex space-x-2">
                <Button variant="outline" className="flex-1">
                  Batafsil
                </Button>
                <Button className="flex-1">
                  Baholash
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default TendersList
