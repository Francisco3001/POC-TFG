package com.devops.tp;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/pokemon")
public class PokemonController {

    private final RestTemplate restTemplate = new RestTemplate();

    @GetMapping("/{name}")
    public String getPokemon(@PathVariable String name) {
        String url = "https://pokeapi.co/api/v2/pokemon/" + name;
        return restTemplate.getForObject(url, String.class);
    }
}