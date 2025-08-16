"""
PubMed Service Module

This module provides functionality to interact with PubMed via the NCBI Entrez API.
It includes functions for searching articles, getting counts, and summarizing data
for use in the InvivoDB dashboard and species pages.
"""

import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

try:
    from Bio import Entrez
    from Bio.Entrez import efetch, esearch, read
except ImportError:
    print("Warning: Biopython not installed. Install with: pip install biopython")
    Entrez = None


@dataclass
class PubMedSummary:
    """Data class for PubMed search results summary"""
    keyword: str
    total_count: int
    recent_count: int  # Last 5 years
    top_journals: List[Tuple[str, int]]
    publication_years: Dict[int, int]
    search_date: datetime


class PubMedService:
    """Service class for PubMed API interactions"""
    
    def __init__(self, email: str = "invivodb@example.com"):
        """
        Initialize the PubMed service
        
        Args:
            email: Email address for NCBI API (required by NCBI)
        """
        if Entrez is None:
            raise ImportError("Biopython is required. Install with: pip install biopython")
        
        self.email = email
        Entrez.email = email
        self.rate_limit_delay = 0.34  # NCBI allows 3 requests per second
    
    def _rate_limit(self):
        """Apply rate limiting to respect NCBI's API limits"""
        time.sleep(self.rate_limit_delay)
    
    def search_articles(self, keyword: str, max_results: int = 100) -> PubMedSummary:
        """
        Search PubMed for articles matching a keyword
        
        Args:
            keyword: Search term (e.g., "Mus musculus", "cancer therapy")
            max_results: Maximum number of results to fetch
            
        Returns:
            PubMedSummary object with search results
        """
        try:
            # Search for articles
            self._rate_limit()
            handle = esearch(db="pubmed", term=keyword, retmax=max_results)
            record = read(handle)
            handle.close()
            
            total_count = int(record["Count"])
            id_list = record["IdList"]
            
            if not id_list:
                return PubMedSummary(
                    keyword=keyword,
                    total_count=0,
                    recent_count=0,
                    top_journals=[],
                    publication_years={},
                    search_date=datetime.utcnow()
                )
            
            # Fetch details for the articles
            self._rate_limit()
            handle = efetch(db="pubmed", id=id_list, rettype="medline", retmode="text")
            articles_data = handle.read()
            handle.close()
            
            # Parse the data (simplified for now)
            summary = self._parse_articles_data(articles_data, keyword, total_count)
            return summary
            
        except Exception as e:
            print(f"Error searching PubMed for '{keyword}': {e}")
            return PubMedSummary(
                keyword=keyword,
                total_count=0,
                recent_count=0,
                top_journals=[],
                publication_years={},
                search_date=datetime.utcnow()
            )
    
    def get_article_count(self, keyword: str) -> int:
        """
        Get the total number of articles for a keyword
        
        Args:
            keyword: Search term
            
        Returns:
            Number of articles
        """
        try:
            self._rate_limit()
            handle = esearch(db="pubmed", term=keyword, retmax=1)
            record = read(handle)
            handle.close()
            return int(record["Count"])
        except Exception as e:
            print(f"Error getting article count for '{keyword}': {e}")
            return 0
    
    def get_species_article_count(self, species_name: str) -> int:
        """
        Get article count for a specific species
        
        Args:
            species_name: Scientific or common name of species
            
        Returns:
            Number of articles
        """
        # Use both scientific and common names for better results
        search_terms = [
            f'"{species_name}"[Title/Abstract]',
            f'"{species_name}"[MeSH Terms]',
            species_name
        ]
        
        total_count = 0
        for term in search_terms:
            count = self.get_article_count(term)
            total_count = max(total_count, count)
            if count > 0:
                break  # Use the first term that returns results
        
        return total_count
    
    def _parse_articles_data(self, articles_data: str, keyword: str, total_count: int) -> PubMedSummary:
        """
        Parse PubMed article data to extract summary information
        
        Args:
            articles_data: Raw MEDLINE data
            keyword: Original search keyword
            total_count: Total number of articles found
            
        Returns:
            PubMedSummary object
        """
        # This is a simplified parser - in a real implementation,
        # you'd want to parse the MEDLINE format more thoroughly
        
        lines = articles_data.split('\n')
        current_year = datetime.utcnow().year
        recent_count = 0
        publication_years = {}
        journals = {}
        
        for line in lines:
            line = line.strip()
            
            # Extract publication year
            if line.startswith('DP  - '):
                year_str = line[6:10]  # Extract year from date
                try:
                    year = int(year_str)
                    publication_years[year] = publication_years.get(year, 0) + 1
                    if year >= current_year - 5:
                        recent_count += 1
                except ValueError:
                    pass
            
            # Extract journal name
            elif line.startswith('JT  - ') or line.startswith('TA  - '):
                journal = line[6:].strip()
                if journal:
                    journals[journal] = journals.get(journal, 0) + 1
        
        # Get top 5 journals
        top_journals = sorted(journals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return PubMedSummary(
            keyword=keyword,
            total_count=total_count,
            recent_count=recent_count,
            top_journals=top_journals,
            publication_years=publication_years,
            search_date=datetime.utcnow()
        )


# Convenience functions for easy use
def get_species_pubmed_count(species_name: str, email: str = "invivodb@example.com") -> int:
    """
    Convenience function to get PubMed article count for a species
    
    Args:
        species_name: Name of the species
        email: Email for NCBI API
        
    Returns:
        Number of PubMed articles
    """
    service = PubMedService(email)
    return service.get_species_article_count(species_name)


def get_keyword_pubmed_summary(keyword: str, email: str = "invivodb@example.com") -> PubMedSummary:
    """
    Convenience function to get detailed PubMed summary for a keyword
    
    Args:
        keyword: Search keyword
        email: Email for NCBI API
        
    Returns:
        PubMedSummary object
    """
    service = PubMedService(email)
    return service.search_articles(keyword)


# Example usage and testing
if __name__ == "__main__":
    # Test the service
    print("Testing PubMed Service...")
    
    # Test species counts
    test_species = ["Mus musculus", "Rattus norvegicus", "Macaca mulatta"]
    
    service = PubMedService()
    
    for species in test_species:
        count = service.get_species_article_count(species)
        print(f"{species}: {count} articles")
    
    # Test detailed search
    summary = service.search_articles("cancer therapy", max_results=50)
    print(f"\nDetailed search for 'cancer therapy':")
    print(f"Total articles: {summary.total_count}")
    print(f"Recent articles (5 years): {summary.recent_count}")
    print(f"Top journals: {summary.top_journals[:3]}") 