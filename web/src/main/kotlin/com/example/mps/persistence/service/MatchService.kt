package com.example.mps.persistence.service

import com.example.mps.domain.model.Match
import com.example.mps.domain.repository.MatchRepository
import org.springframework.data.domain.Page
import org.springframework.data.domain.PageRequest
import org.springframework.stereotype.Service

@Service
class MatchService(
    private val repository: MatchRepository
) {

    fun getMatches(page: Int = 0): Page<Match> {
        val p = PageRequest.of(page, 50)
        return repository.findAll(p).map { it.toMatch() }
    }
}